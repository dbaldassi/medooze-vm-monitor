
import { logger, StatsComponent } from '../stats.js';
import { DuckDBConnection, DuckDBDataChunk, DuckDBMaterializedResult, VARCHAR, INTEGER, DOUBLE } from 'npm:@duckdb/node-api';

type PublisherStats = {
    publisher_bitrate: number;
    publisher_fps: number;
    publisher_res: string;
    publisher_rtt: number;
    publisher_pc_state: number;
    publisher_viewer_count: number;
}

export class PublisherStatsComponent implements StatsComponent {
    public info: PublisherStats;

    constructor() {
        this.info = new PublisherStats;
    }

    public fetch(): void {}

    public create_table(conn: DuckDBConnection): Promise<DuckDBMaterializedResult> {
        return conn.run(`
CREATE TABLE IF NOT EXISTS publisher_stats (
    exp_name                    VARCHAR,
    date                        VARCHAR,
    TIME                        BIGINT,
    "PUBLISHER BITRATE"         BIGINT,
    "PUBLISHER FPS"             BIGINT,
    "PUBLISHER RESOLUTION"      VARCHAR,
    "PUBLISHER RTT"             BIGINT,
    "CONNECTION STATE"          BIGINT,
    "VIEWER COUNT"              BIGINT,
    );
`);
    }

    public drop_table(conn: DuckDBConnection): void {}

    public update_table(metadata: TableMetadata): void {
        logger.append_to_table({
            name: 'publisher_stats',
            types: [VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, VARCHAR, INTEGER, INTEGER, INTEGER],
            values: [[metadata.exp_name, metadata.date, metadata.info.time, this.info.publisher_bitrate, this.info.publisher_fps,
                      this.info.publisher_res, this.info.publisher_rtt, this.info.publisher_pc_state, this.info.viewer_count
                     ]]
        });
    }
}
