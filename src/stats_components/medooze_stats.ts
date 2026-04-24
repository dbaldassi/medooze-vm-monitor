
import { logger, StatsComponent } from '../stats.js';
import { DuckDBConnection, DuckDBDataChunk, DuckDBMaterializedResult, VARCHAR, INTEGER, DOUBLE } from 'npm:@duckdb/node-api';

type MedoozeStats = {
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

export class MedoozeStatsComponent implements StatsComponent {
    public info: MedoozeStats;

    constructor() {
        this.info = new MedoozeStats;
    }

    public fetch(): void {}

    public create_table(conn: DuckDBConnection): Promise<DuckDBMaterializedResult> {
        return conn.run(`
CREATE TABLE IF NOT EXISTS medooze_stats (
    exp_name                     VARCHAR,
    date                        VARCHAR,
    TIME                        BIGINT,
    "MEDOOZE INCOMING LOST"     BIGINT,
    "MEDOOZE INCOMING DROP"     BIGINT,
    "MEDOOZE INCOMING BITRATE"  BIGINT,
    "MEDOOZE INCOMING NACK"     BIGINT,
    "MEDOOZE INCOMING PLI"      BIGINT,
    );
`);
    }

    public drop_table(conn: DuckDBConnection): void {}

    public update_table(metadata: TableMetadata): void {
        logger.append_to_table({
            name: 'medooze_stats',
            types: [VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER],
            values: [[metadata.exp_name, metadata.date, metadata.time,
                      this.info.medooze_incoming_lost, this.info.medooze_incoming_drop,
                      this.info.medooze_incoming_bitrate, this.info.medooze_incoming_nack, this.info.medooze_incoming_pli
                     ]]
        });
    }

}
