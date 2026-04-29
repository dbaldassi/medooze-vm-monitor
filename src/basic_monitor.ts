import { Monitor, MonitorConfig } from './monitor.ts';
import { logger } from './stats.ts';

export class BasicMonitor extends Monitor {
    constructor(monitor_config: MonitorConfig) {
        super(monitor_config);
    }

    protected override on_start(): void {
        console.log("Start");
        logger.start_collection();
    }

    protected override on_stop(): void {
        console.log("stop");
        logger.stop_collection();
    }
    
    required_step(_: string) {
        // nothing
    }
}
