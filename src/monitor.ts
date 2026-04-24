
import { SystemManager } from './system_manager.ts';
import { logger } from './stats.ts';

type RunConfig = {
    repet: number;
    scenario: string;
    params: object;
    domain: string;
}

export type MonitorConfig = {
    runs: [RunConfig];
    monitor_type: string;
    progress_host: string;
    progress_port: number;
}

type Scenario = {
    name: string;
    steps: [any];
}

export abstract class Monitor {
    protected system_manager: SystemManager;
    protected monitor_config: MonitorConfig;

    constructor(monitor_config: MonitorConfig) {
        this.system_manager = new SystemManager;
        this.monitor_config = monitor_config;
    }

    protected abstract required_step(step: string) : void

    // legacy
    protected save(opt: any) {}
    protected exit() {}

    private async run_scenar(scenar: Scenario) {
        logger.set_exp_name(scenar.name);

        for(let step of scenar.steps) {
            // Await for requirement to be fullfilled before performing the step
            if(step.require) {
                this.required_step(step.require);
            }

            // Number of times to repeat this step
            let repeat = step.repeat ?? 1;
            for(let i = 0; i < repeat; ++i) {
                // Perform all actions contained in this step
                step.actions.forEach(action => this[action](step[action]));

                // If the step speficieda wait time before going to next step
                if(step.wait) {
                    // Create promise with timout to wait
                    const promise = new Promise((resolve, reject) => {
                        setTimeout(() => { resolve(); }, step.wait);
                    });
                    // Wait for timout to expire
                    await promise;
                }
            }
        }
    }

    public async run() {
        for(let r of this.monitor_config.runs) {
            this.system_manager.set_domain(r.domain);

            for(let i = 0; i < r.repet; ++i) {
                this.system_manager.start_vm();

                const scenario = await import(`../scenario/${r.scenario}.json`);
                const template = parse(scenario);

                // for number parameters set number because we can only set string in json for template parameters
                for(let param of template.parameters) {
                    if(param.defaultValue) {
                        let value = parseInt(param.defaultValue);
                        if(!Number.isNaN(value)) param.defaultValue = value;
                    }
                }

                await this.run_scenar(template(r.params));

                this.system_manager.stop_vm();
            }
        }
    }
}
