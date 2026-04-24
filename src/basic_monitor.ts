import { Monitor, MonitorConfig } from './monitor.ts';
import { logger } from './stats.ts';

export class BasicMonitor extends Monitor {
    constructor(monitor_config: MonitorConfig) {
        super(monitor_config);
    }

    required_step(requirement: string) {
        // nothing
    }
}
