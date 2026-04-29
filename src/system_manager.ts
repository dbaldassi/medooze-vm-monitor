import Path from "node:path";
import FS from "node:fs";
import os from 'npm:os-utils';

import { exec, execSync } from 'node:child_process';
import { StatsListener, CgroupStatsComponent } from './stats_components/cgroup_stats.ts';
import { VirshStatsComponent } from './stats_components/virsh_stats.ts';
import { logger } from './stats.ts';

import config from '../config/config.json' with { type: 'json' };

// Units
const KILO: number = 1024;
const MEGA:number = 1024 * KILO;
const GIGA: number = 1024 * MEGA;
const SECONDS: number = 1000;

function clamp(value: number, lower: number, upper: number): number {
    return Math.min(Math.max(value, lower), upper);
}

type Pid = {
    kp: number;
    ki: number;
    kd: number;

    prevError: number;
    integrator: number;
    dt: number;
}

export class SystemManager implements StatsListener {
    private ram_usage_path: string = "";
    private ram_total_path: string = "";
    private swap_usage_path: string = "";
    private swap_event_path: string = "";
    private memory_event_path: string = "";
    private memory_pressure_path: string = "";
    private memory_reclaim_path: string = "";
    private memory_stat_file: string = "";

    private swappiness: number;
    private pid: Pid;
    private window_size: number = 30;
    private inactive_anon_values: number[] = [];
    private threshold_percentage: number = 1;

    private domain: string = "";

    private cgroup_stats: CgroupStatsComponent;
    private virsh_stats: VirshStatsComponent;

    private cgroup_path: string;

    constructor() {
        this.cgroup_path = "";

        this.cgroup_stats = new CgroupStatsComponent(this);
        this.virsh_stats = new VirshStatsComponent(this);

        logger.register_component(this.cgroup_stats);
        logger.register_component(this.virsh_stats);

        this.swappiness = 0;

        this.pid = {
            kp : 1/10, // to be tuned
            ki : 0/10, // to be tuned
            kd : 10/10, // to be tuned

            prevError : 0,
            integrator : 0,

            dt : 10 // 10sec
        };
    }

    public set_domain(domain: string) {
        this.domain = domain;
    }

    private fetch_swap_stats() {
        try {
            const data = FS.readFileSync('/proc/vmstat', 'utf8');
            const lines = data.split('\n');
            for (const line of lines) {
                const [key, value] = line.split(/\s+/);
                if (key === 'pswpin') {
                    this.cgroup_stats.info.swapin = parseInt(value);
                } else if (key === 'pswpout') {
                    this.cgroup_stats.info.swapout = parseInt(value);
                } else if (key === 'pgpgin') {
                    this.cgroup_stats.info.pgpgin = parseInt(value);
                } else if (key === 'pgpgout') {
                    this.cgroup_stats.info.pgpgout = parseInt(value);
                }
            }
        } catch (e) {
            console.error("Error reading /proc/vmstat:", e);
            this.cgroup_stats.info.swapin = 0;
            this.cgroup_stats.info.swapout = 0;
        }
    }

    private fetch_ram_usage() {
        try {
            // Read current memory usage from cgroup file
            const data = FS.readFileSync(this.ram_usage_path, 'utf8');
            this.cgroup_stats.info.ram_usage = parseInt(data) / MEGA;
        } catch(e) {
            this.cgroup_stats.info.ram_usage = 0;
        }
    }

    private fetch_ram_free() {
        try {
            const data = FS.readFileSync(this.ram_total_path, 'utf8');
            this.cgroup_stats.info.ram_free = parseInt(data) / MEGA - this.cgroup_stats.info.ram_usage;
        } catch(e) {
            this.cgroup_stats.info.ram_free = 0;
        }
    }

    private fetch_swap_usage() {
        try {
            const data = FS.readFileSync(this.swap_usage_path, 'utf8');
            this.cgroup_stats.info.swap_usage = parseInt(data) / MEGA;
        } catch(e) {
            this.cgroup_stats.info.swap_usage = 0;
        }
    }

    private fetch_mem_stat() {
        try {
            const data = FS.readFileSync(this.memory_stat_file, 'utf8');

            for(const line of data.toString().split('\n')) {
                const split = line.split(' ');
                this.cgroup_stats.info[split[0] as keyof typeof this.cgroup_stats.info] = parseInt(split[1]);
            }
        } catch(e) {
            console.error(e);
        }
    }

    private fetch_cpu_and_load() {
        try {
            // Récupérer le load average
            const loadAverage = os.loadavg(1); // Load average sur 1 minute
            this.cgroup_stats.info.load_average = loadAverage;

            // Récupérer l'utilisation du CPU
            os.cpuUsage((cpuUsage: number) => {
                this.cgroup_stats.info.host_cpu = cpuUsage * 100; // Convertir en pourcentage
                console.log(`Load Average: ${loadAverage}, CPU Usage: ${cpuUsage * 100}%`);
            });
        } catch (e) {
            console.error("Error fetching CPU and Load Average:", e);
            this.cgroup_stats.info.load_average = 0;
            this.cgroup_stats.info.host_cpu = 0;
        }
    }

    private get_reclaimable_bytes(): number {
        let cgroup_reclaimable = (this.cgroup_stats.info.slab_reclaimable + this.cgroup_stats.info.inactive_file) / (1024 * 1024);

        return cgroup_reclaimable;
    }

    private fetch_memory_pressure() {
        try {
            const data = FS.readFileSync(this.memory_pressure_path);
            const some = data.toString().split('\n')[0];
            const pressure = some.split(' ');


            for(let p of pressure) {
                const fields = p.split('=');
                if(fields.length === 2) {
                    this.cgroup_stats.info[`pressure_${fields[0]}` as keyof typeof this.cgroup_stats.info] = parseFloat(fields[1]);
                }
            }
        } catch(e) {}
    }

    private fetch_virsh_info() {
        exec(`virsh dommemstat --domain ${this.domain}`, (err, output) => {
            if(err) {
                this.virsh_stats.info.virsh_actual = 0;
                console.error(err);
                return;
            }

            const lines = output.split('\n');
            for(const line of lines) {
                const splitted = line.split(' ');
                if(splitted.length === 2) {
                    this.virsh_stats.info[`virsh_${splitted[0]}` as keyof typeof this.virsh_stats.info] = parseInt(splitted[1]);
                }
            }
        });
    }

    public fetch() {
        this.fetch_ram_usage();
        this.fetch_ram_free();
        this.fetch_swap_usage();
        this.fetch_memory_pressure();
        this.fetch_virsh_info();
        this.fetch_mem_stat();
        this.fetch_swap_stats();
        this.fetch_cpu_and_load();
    }

    private get_domain_pid(): number | undefined {
        const out = SystemManager.quick_exec_sync(`pgrep -f "/usr/bin/qemu-system-x86_64 -name guest=${this.domain}"`, {});

        if(out) {
            return parseInt(out);
        }

        return undefined;
    }

    private setup_cgroup() {
        const pid = this.get_domain_pid();
        if(pid === undefined) return;

        const data = FS.readFileSync(`/proc/${pid}/cgroup`, 'utf8');
        const split = data.split(':');

        const path = split[2].split('/');
        path.pop(); // remove /emulator
        path.pop(); // remove /libvirt

        this.cgroup_path = `/sys/fs/cgroup/${path.join("/")}`;

        this.ram_usage_path  = Path.join(this.cgroup_path, config.ram_usage_file);
        this.ram_total_path  = Path.join(this.cgroup_path, config.ram_total_file);
        this.swap_usage_path = Path.join(this.cgroup_path, config.swap_usage_file);
        this.swap_event_path = Path.join(this.cgroup_path, config.swap_event_file);
        this.memory_event_path = Path.join(this.cgroup_path, config.memory_event_file);
        this.memory_pressure_path = Path.join(this.cgroup_path, config.memory_pressure_file);
        this.memory_reclaim_path = Path.join(this.cgroup_path, config.memory_reclaim_file);
        this.memory_stat_file = Path.join(this.cgroup_path, config.memory_stat_file);

        console.log(this.ram_usage_path);
    }

    public start_vm() {
        SystemManager.quick_exec_sync(`virsh start ${this.domain}`, {});
        this.setup_cgroup();
    }

    public stop_vm(): Promise<void> {
        SystemManager.quick_exec_sync(`virsh shutdown ${this.domain}`, {});

        return new Promise<void>(resolve => resolve());
    }

    private pid_regul(target: number, measured: number): number {
        const error = target - measured;

        this.pid.integrator += error * this.pid.dt;

        const p = this.pid.kp * error;
        const i = this.pid.ki * this.pid.integrator;
        const d = this.pid.kd * (this.pid.prevError - error) / this.pid.dt;

        const out = p + i + d;

        this.pid.prevError = error;

        return out;
    }

    // Max in MiB, need to be root
    public set_max_ram(max: number) {
        max = Math.max(max, 0); // don't write negative value
        // Write new max in the file

        try {
            FS.writeFile(this.ram_total_path, String(max * MEGA), (err) => {
                if(err) console.error(err);
                else {
                    console.log("Wrote ", max);
                    this.cgroup_stats.info.maxram = max;
                }
            });
        } catch(error) {
            console.error(error);
        }
    }

    public reclaim_memory(mem: number, swappiness: number|undefined): boolean {

        try {
            let cmd = `${mem*1024*1024}`
            if(swappiness !== undefined) {
                cmd = `${cmd} swappiness=${swappiness}`;
            }

            console.log("Reclaiming", cmd);

            this.cgroup_stats.info.maxram += 100; // mark to find where we begin reclaim when boxing plot

            FS.writeFile(this.memory_reclaim_path, cmd, (err) => {
                if(err) console.error(err);
            });
        } catch(error) {
            console.error(error);
            return false;
        }

        return true;
    }

    public memory_reduction(increment: number, threshold: number, increase: number): void {
        const vm_mem = (this.virsh_stats.info.virsh_available - this.virsh_stats.info.virsh_usable) / 1024;

        console.log(this.cgroup_stats.info.ram_usage, (vm_mem + 2 * increment));
        if(this.cgroup_stats.info.swap_usage == 0 && this.cgroup_stats.info.ram_free > threshold) {
            this.set_max_ram(this.cgroup_stats.info.ram_usage + threshold / 2); // remove all free memory at the beginning
        }

        if(this.cgroup_stats.info.ram_usage > vm_mem + threshold) {
            this.set_max_ram(this.cgroup_stats.info.maxram - increment); // Progressively decrease max memory
        }
        else if(!!increase && this.cgroup_stats.info.ram_usage <  (vm_mem + threshold / 10)) {
            this.set_max_ram(this.cgroup_stats.info.maxram + increase);
        }
    }

    private update_anon_window() {
        if(this.inactive_anon_values === undefined) {
            console.log("create anon array");
            this.inactive_anon_values = [];
        }

        if(this.cgroup_stats.info.inactive_anon === undefined) {
            return; // no data
        }

        this.inactive_anon_values.push(this.cgroup_stats.info.inactive_anon);

        if(this.inactive_anon_values.length < this.window_size) {
            console.log("not enough values");
            return; // window not filled yet, considered not stabilized
        }
        else if(this.inactive_anon_values.length > this.window_size) {
            this.inactive_anon_values.shift(); // we want only the last minute not one second more
        }
    }

    private calculate_standard_seviation(values: number[]) {
        const mean = values.reduce((a:  number, b: number) => a + b, 0) / values.length;
        const variance = values.reduce((a: number, b: number) => a + Math.pow(b - mean, 2), 0) / values.length;
        return Math.sqrt(variance);
    }

    public cgroups_regul(threshold: number, dt: number) {
        this.update_anon_window();

        const unused = this.cgroup_stats.info.ram_usage - (this.cgroup_stats.info.vm_free_used + this.cgroup_stats.info.vm_free_bufcache);

        if(unused === undefined || Number.isNaN(unused) || unused < threshold) {
            console.log("unused is NaN or greater than threshold");
            return;
        }

        const inactive_anon = this.cgroup_stats.info.inactive_anon / (1024 * 1024);

        if(inactive_anon === 0) {
            console.log("anon is 0, reclaiming 100");
            this.reclaim_memory(15, undefined); // to be adjusted in function of reclaimable bytes
            return;
        }

        if(this.inactive_anon_values.length < this.window_size) {
            console.log("Not enough values yet");
            return; // not enough values yet
        }

        const std_dev = this.calculate_standard_seviation(this.inactive_anon_values);

        // Vérifier si l'écart type est inférieur à un seuil
        if (std_dev >= 1) {
            console.log("Not stabilized (stdDev too high):", std_dev);
            return; // Pas encore stabilisé
        }

        this.inactive_anon_values = [];

        this.reclaim_memory(Math.min(100,unused - threshold), undefined);
    }

    public ballon_regul(threshold: number, dt: number): number {
        threshold *= 1024;

        const max = 4 * 1024 * 1024 - (this.virsh_stats.info.virsh_available - this.virsh_stats.info.virsh_usable); // max ram is 4GB
        const min = 0;
        this.pid.dt = dt;

        const target = clamp(threshold + (this.virsh_stats.info.virsh_swap_out - this.virsh_stats.info.virsh_swap_in), min, max);

        let out = this.pid_regul(target, this.virsh_stats.info.virsh_usable);

        out = ((this.virsh_stats.info.virsh_usable + out < target) ? target - this.virsh_stats.info.virsh_usable : Math.floor(out));

        const LIMIT = 300;
        if(out < -LIMIT * 1024) {
            out = Math.sign(out) * LIMIT * 1024; // limit to 200K
        }

        let new_vm_size = Math.floor(clamp(this.virsh_stats.info.virsh_actual + out, target, 4 * 1024 * 1024));

        let time = 3;
        if(out < 0) {
            time = (1 / 250) * (out / -1024) + 1/2; // found by interpolation
            time = Math.max(time, 5); // min 1 sec because virsh report stats every second
        }

        SystemManager.quick_exec(`virsh setmem --domain ${this.domain} --size ${new_vm_size}K --current`, {});

        return time;
    }

    public memory_reclaim(increment: number, threshold: number, swappiness: number) {
        const vm_mem = (this.virsh_stats.info.virsh_available - this.virsh_stats.info.virsh_usable) / 1024;

        if(this.cgroup_stats.info.ram_usage > vm_mem + threshold) {
            this.reclaim_memory(increment, swappiness);
        }
    }

    public set_balloon_size(size: number) {
        SystemManager.quick_exec(`virsh setmem --domain ${this.domain} --size ${size}K --current`, {});
    }

    static quick_exec(cmd: string, opts: any) {
        exec(cmd, opts, (err, output) => {
            if(err) console.error(err);
            else console.log(output);
        });
    }

    static quick_exec_sync(cmd: string, opts: any): string|undefined {
        try {
            const proc = new Deno.Command("sh", {
                args: ["-c", cmd],
                stdout: "piped",
                stderr: "piped"
            });

            const result = proc.outputSync();
            const stdout = new TextDecoder().decode(result.stdout);
            console.log(stdout);
            return stdout;
        } catch(err: any) {
            console.error(`Error executing : ${cmd} : `, err);
        }
    }
}
