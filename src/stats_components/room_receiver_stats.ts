
import { logger, StatsComponent } from '../stats.js';
import { DuckDBConnection, DuckDBDataChunk, DuckDBMaterializedResult, VARCHAR, INTEGER, DOUBLE } from 'npm:@duckdb/node-api';

type RoomReceiversStats = {}

export class RoomReceiversStatsComponent implements StatsComponent {
    public info: RoomReceiversStats;

    constructor() {
        this.info = new RoomReceiversStats;
    }

    public fetch(): void {}

    public create_table(conn: DuckDBConnection): Promise<DuckDBMaterializedResult> {
        return conn.run(`
CREATE TABLE IF NOT EXISTS room_receivers(
    exp_name VARCHAR,
    date VARCHAR,
    room_id VARCHAR,
    TIME BIGINT,
    participant_id VARCHAR,
    receiving_participant_id VARCHAR,
    BITRATE BIGINT,
    RTT BIGINT,
    FPS BIGINT
    )
`);
    }

    public drop_table(conn: DuckDBConnection): void {}

    public update_table(metadata: TableMetadata): void {

    }
}
