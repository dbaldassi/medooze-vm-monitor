
import { DuckDBInstance, DuckDBConnection, DuckDBDataChunk, DuckDBMaterializedResult, VARCHAR, INTEGER, DOUBLE } from 'npm:@duckdb/node-api';
import config from '../config/config.json' with { type: 'json' };

export type TableMetadata = {
    exp_name: string;
    date: string;
    time: number;
}

export interface StatsComponent {
    fetch(): void;
    create_table(conn: DuckDBConnection): Promise<DuckDBMaterializedResult>;
    drop_table(conn: DuckDBConnection): void;
    update_table(conn: DuckDBConnection, metadata: TableMetadata): void;
}

class StatsLogger {
    private metadata: TableMetadata;
    private components: [StatsComponents];

    constructor() {
        this.setup_duckdb();
        this.metadata.time = 0;
    }

    public set_exp_name(name: string): void {
        this.metadata.exp_name = name;
        this.metadata.date = new Date().toLocaleString('fr-FR').replaceAll(' ', '-').replaceAll('/', '-').replaceAll(':', '-');
    }

    public async register_component(component: StatsComponent): void {
        await this.duck_promise.promise;

        await component.create_teable(this.connection);

        this.components.push(component);
    }

    public unregister_component(component: StatsComponent) {
        this.component.splice(this.component.indexOf(component), 1);
    }

    async setup_duckdb(): void {
        this.duck_promise = Promise.withResolvers();

        this.instance = await DuckDBInstance.create('results.db');
        this.connection = await this.instance.connect()

        this.duck_promise.resolve();
    }

    public async append_to_table(table_config) {
        const appender = await this.connection.createAppender(table_config.name);
        const chunk = DuckDBDataChunk.create(table_config.types);
        chunk.setRows(table_config.values);

        appender.appendDataChunk(chunk);
        appender.flushSync();
    }

    public async log_info() {
        await this.duck_promise.promise;

        this.metadata.time += config.time_interval;

        this.components.forEach(component => {
            component.fetch();
            component.update_table(this.metadata);
        });
    }
}

// glogbal / singleton
export var logger = new StatsLogger;
