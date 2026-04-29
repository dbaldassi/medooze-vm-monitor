
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
    update_table(metadata: TableMetadata): void;
}

class StatsLogger {
    private metadata: TableMetadata;
    private instance?: DuckDBInstance;
    private connection?: DuckDBConnection;
    private components: StatsComponent[];
    private duck_promise: any = undefined;
    private collector: number;

    constructor() {
        this.setup_duckdb();
        this.metadata = {
            time: 0,
            exp_name: "",
            date: ""
        };
        this.components = [];
        this.collector = 0;
    }

    public set_exp_name(name: string): void {
        this.metadata.exp_name = name;
        this.metadata.date = new Date().toLocaleString('fr-FR').replaceAll(' ', '-').replaceAll('/', '-').replaceAll(':', '-');
        this.metadata.time = 0;
    }

    public async register_component(component: StatsComponent) {
        await this.duck_promise.promise;

        await component.create_table(this.connection as DuckDBConnection);

        this.components.push(component);
    }

    public unregister_component(component: StatsComponent) {
        this.components.splice(this.components.indexOf(component), 1);
    }

    async setup_duckdb() {
        this.duck_promise = Promise.withResolvers();

        this.instance = await DuckDBInstance.create('results.db');
        this.connection = await this.instance.connect()

        this.duck_promise.resolve();
    }

    public async append_to_table(table_config: any) {
        const appender = await this.connection?.createAppender(table_config.name);
        const chunk = DuckDBDataChunk.create(table_config.types);
        chunk.setRows(table_config.values);

        appender?.appendDataChunk(chunk);
        appender?.flushSync();
    }

    public async log_info() {
        await this.duck_promise.promise;

        this.components.forEach(component => {
            component.fetch();
            component.update_table(this.metadata);
        });
    }

    public start_collection(): void {
        this.collector = setInterval(() => {
            this.metadata.time += config.time_interval;
            this.log_info();
        }, config.time_interval);
    }

    public stop_collection(): void {
        clearTimeout(this.collector);
    }
}

// glogbal / singleton
export const logger = new StatsLogger;
