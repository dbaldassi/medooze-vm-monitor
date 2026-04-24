
import { logger, StatsComponent } from '../stats.js';
import { DuckDBConnection, DuckDBDataChunk, DuckDBMaterializedResult, VARCHAR, INTEGER, DOUBLE } from 'npm:@duckdb/node-api';

type ViewerStats = {
    target: number;
    bitrate: number;
    rtt: number;
    e2e: number;
    fps: number;
    res: string;
    rid: string;
}

export class ViewersStatsComponent implements StatsComponent {
    public viewers: Map<string, ViewerStats>;

    constructor() {
        this.info = new Map<string, ViewerStats>();
    }

    public fetch(): void {}

    public create_table(conn: DuckDBConnection): Promise<DuckDBMaterializedResult> {
        return conn.run(`
CREATE TABLE IF NOT EXISTS viewers_stats (
    exp_name VARCHAR,
    date VARCHAR,
    client_id VARCHAR,
    TIME INTEGER,
    target INTEGER,
    bitrate INTEGER,
    rtt INTEGER,
    delay INTEGER,
    fps INTEGER,
    resolution VARCHAR,
    rid VARCHAR
    );
`);
    }

    public drop_table(conn: DuckDBConnection): void {}

    public update_table(metadata: TableMetadata): void {
        let viewer_rows = [];
        this.viewers.forEach((v,k) => viewer_rows.push([metadata.exp_name, metadata.date, k, metadata.time, v.target, v.bitrate, v.rtt, v.e2e, v.fps, v.res, v.rid]));
        logger.append_to_table({
            name: 'viewers_stats',
            types: [VARCHAR, VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, VARCHAR, VARCHAR],
            values: viewer_rows
        })
    }

}
