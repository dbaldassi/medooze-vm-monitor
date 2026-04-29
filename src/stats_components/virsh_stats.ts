
import { logger, StatsComponent } from '../stats.ts';
import type { TableMetadata } from '../stats.ts';
import { DuckDBConnection, DuckDBDataChunk, DuckDBMaterializedResult, VARCHAR, INTEGER, DOUBLE } from 'npm:@duckdb/node-api';
import { StatsListener } from './cgroup_stats.ts';

type VirshStats = {
    virsh_actual: number;
    virsh_unused: number;
    virsh_usable: number;
    virsh_available: number;
    virsh_swap_in: number;
    virsh_swap_out: number;
    virsh_minor_fault: number;
    virsh_major_fault: number;
}

export class VirshStatsComponent implements StatsComponent {
    public info: VirshStats;
    private listener: StatsListener;

    constructor(listener: StatsListener) {
        this.info = {
            virsh_actual: 0,
            virsh_unused: 0,
            virsh_usable: 0,
            virsh_available: 0,
            virsh_swap_in: 0,
            virsh_swap_out: 0,
            virsh_minor_fault: 0,
            virsh_major_fault: 0,
        };
        this.listener = listener;
    }

    public fetch(): void {
        this.listener.fetch();
    }

    public create_table(conn: DuckDBConnection): Promise<DuckDBMaterializedResult> {
        return conn.run(`
CREATE TABLE IF NOT EXISTS virsh_stats (
    exp_name                  VARCHAR,
    date                      VARCHAR,
    TIME                      BIGINT,
    "VIRSH ACTUAL"            BIGINT,
    "VIRSH UNUSED"            BIGINT,
    "VIRSH USABLE"            BIGINT,
    "VIRSH AVAILABLE"         BIGINT,
    "VIRSH SWAP IN"           BIGINT,
    "VIRSH SWAP OUT"          BIGINT,
    "VIRSH MINOR FAULT"       BIGINT,
    "VIRSH MAJOR FAULT"       BIGINT,
    );
`);
    }

    public drop_table(conn: DuckDBConnection): void {

    }

    public update_table(metadata: TableMetadata): void {
        logger.append_to_table({
            name: 'virsh_stats',
            types: [VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER],
            values: [[metadata.exp_name, metadata.date, metadata.time,
             this.info.virsh_actual, this.info.virsh_unused, this.info.virsh_usable,
             this.info.virsh_available, this.info.virsh_swap_in, this.info.virsh_swap_out,
             this.info.virsh_minor_fault, this.info.virsh_major_fault]]
        });
    }

}
