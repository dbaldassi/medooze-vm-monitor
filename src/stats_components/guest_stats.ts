
import { logger, StatsComponent } from '../stats.js';
import { DuckDBConnection, DuckDBDataChunk, DuckDBMaterializedResult, VARCHAR, INTEGER, DOUBLE } from 'npm:@duckdb/node-api';

type GuestStats = {
    vm_ram_usage: number;
    vm_ram_free: number;
    vm_cpu_usage: number;
    vm_free_total: number;
    vm_free_used: number;
    vm_free_bufcache: number;
    rx_packet: number;
    rx_dropped: number;
    rx_errors: number;
    rx_missed: number;
    tx_packet: number;
    tx_dropped: number;
    tx_errors: number;
    tx_missed: number;
}

export class GuestStatsComponent implements StatsComponent {
    public info: GuestStats;

    constructor() {
        this.info = new GuestStats;
    }

    public fetch(): void {}

    public create_table(conn: DuckDBConnection): Promise<DuckDBMaterializedResult> {
        return conn.run(`
CREATE TABLE IF NOT EXISTS guest_stats (
    exp_name                    VARCHAR,
    date                        VARCHAR,
    TIME                        BIGINT,
    "VM MEMORY USAGE"           BIGINT,
    "VM MEMORY FREE"            BIGINT,
    "VM CPU USAGE"              DOUBLE,
    "VM FREE TOTAL"             DOUBLE,
    "VM FREE USED"              DOUBLE,
    "VM FREE BUFCACHE"          DOUBLE,
    "RX PACKET"                 BIGINT,
    "RX DROPPED"                BIGINT,
    "RX ERRORS"                 BIGINT,
    "RX MISSED"                 BIGINT,
    "TX PACKET"                 BIGINT,
    "TX DROPPED"                BIGINT,
    "TX ERRORS"                 BIGINT,
    "TX MISSED"                 BIGINT,
    );
`);
    }

    public drop_table(conn: DuckDBConnection): void {}

    public update_table(metadata: TableMetadata): void {
        logger.append_to_table({
            name: 'guest_stats',
            types: [VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, DOUBLE, DOUBLE, DOUBLE, DOUBLE, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER],
            values: [[metadata.exp_name, metadata.date, metadata.time,
                      this.info.vm_ram_usage, this.info.vm_ram_free, this.info.vm_cpu_usage,
                      this.info.vm_free_total, this.info.vm_free_used, this.info.vm_free_bufcache,
                      this.info.rx_packet, this.info.rx_dropped, this.info.rx_missed, this.info.rx_errors,
                      this.info.tx_packet, this.info.tx_dropped, this.info.tx_missed, this.info.tx_errors
                     ]]
        });
    }

}
