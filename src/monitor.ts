
import { SystemManager } from './system_manager.ts';
import { logger } from './stats.ts';
import fs from "node:fs";
import parse from 'npm:json-templates';

type RunConfig = {
    repet: number;
    scenario: string;
    params: object;
    domain: string;
}

export type MonitorConfig = {
    runs: RunConfig[];
    monitor_type: string;
    progress_host: string;
    progress_port: number;
}

type Scenario = {
    name: string;
    steps: any[];
}

export abstract class Monitor {
    protected system_manager: SystemManager;
    protected monitor_config: MonitorConfig;

    constructor(monitor_config: MonitorConfig) {
        this.system_manager = new SystemManager;
        this.monitor_config = monitor_config;
    }

    protected abstract required_step(step: string) : Promise<void> | undefined;
    protected abstract on_start(): void;
    protected abstract on_stop(): void;

    // legacy
    protected save(_opt: any) {}
    protected exit() {}

    private async run_scenar(scenar: Scenario) {
        logger.set_exp_name(scenar.name);

        this.on_start();

        for(const step of scenar.steps) {
            // Await for requirement to be fullfilled before performing the step
            if(step.require) {
                const promise = this.required_step(step.require);
                if(promise) await promise;
            }

            // Number of times to repeat this step
            const repeat = step.repeat ?? 1;
            for(let i = 0; i < repeat; ++i) {
                // Perform all actions contained in this step
                step.actions.forEach((action: keyof this) => (this[action] as Function)(step[action]));

                // If the step speficieda wait time before going to next step
                if(step.wait) {
                    // Create promise with timout to wait
                    const promise = new Promise<void>((resolve) => {
                        setTimeout(() => { resolve(); }, step.wait);
                    });
                    // Wait for timout to expire
                    await promise;
                }
            }
        }

        this.on_stop();
        console.log("End scenar");
    }

    public async run() {
        for(const r of this.monitor_config.runs) {
            this.system_manager.set_domain(r.domain);

            for(let i = 0; i < r.repet; ++i) {
                this.system_manager.start_vm();
                const data = fs.readFileSync(`./scenario/${r.scenario}.json`, 'utf8');
                const scenario = JSON.parse(data);
                const template = parse(scenario);

                // for number parameters set number because we can only set string in json for template parameters
                for(const param of template.parameters) {
                    if(param.defaultValue) {
                        const value = parseInt(param.defaultValue);
                        if(!Number.isNaN(value)) param.defaultValue = value;
                    }
                }

                await this.run_scenar(template(r.params));
                console.log("Run out scenar");

                this.system_manager.stop_vm();
            }
        }
        console.log("Running out");
    }
}
