import { Monitor, MonitorConfig } from './monitor.ts';
import { logger } from './stats.ts';

const SECONDS: number = 1000;

export class BasicMonitor extends Monitor {
    private virsh_ready_promise: PromiseWithResolvers<void>;
    private pid_balloon_timeout: number = 0;
    
    constructor(monitor_config: MonitorConfig) {
        super(monitor_config);

        this.virsh_ready_promise = Promise.withResolvers();
        this.system_manager.addEventListener("virsh_ready", () => this.virsh_ready_promise.resolve());
    }

    protected override on_start(): void {
        logger.start_collection();
    }

    protected override on_stop(): void {
        logger.stop_collection();
    }

    public start_balloon_regul(opts: any) {
        console.log("Start regul");
        // let params = opts.pid;
        // trasnform params into float
        // console.log(params, this.system_manager.pid);
        /*
          this.sys_manager.pid.kp = parseFloat(params.kp);
          this.sys_manager.pid.ki = parseFloat(params.ki);
          this.sys_manager.pid.kd = parseFloat(params.kd);
        */
        let time = opts.timeout;
        const callback = () => {
            time = this.system_manager.ballon_regul(opts.threshold, time);
            this.pid_balloon_timeout = setTimeout(callback, Math.floor(time * SECONDS));
        };

        this.pid_balloon_timeout = setTimeout(callback, time * SECONDS);
    }

    stop_balloon_regul() {
        console.log("Stop regul");
        clearTimeout(this.pid_balloon_timeout);
    }

    protected override required_step(step: string): Promise<void> | undefined {
        console.log("Required step");
        if(step === "virsh_ready") {
            return this.virsh_ready_promise.promise;
        }
    }
}
