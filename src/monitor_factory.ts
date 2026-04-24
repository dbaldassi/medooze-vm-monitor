import { Monitor } from './monitor.ts'
import { MedoozeMonitor } from './monitor_medooze.ts'
import { BasicMonitor } from './basic_monitor.ts';

export class MonitorFactory {
    public static create(monitor_config: MonitorConfig): Monitor {
        if (monitor_config.monitor_type === "basic") {
            return new BasicMonitor(monitor_config);
        }
        else if(monitor_config.monitor_type === "medooze") {
            return new MedoozeMonitor(monitor_config);
        }
    }
}
