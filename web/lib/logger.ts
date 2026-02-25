import fs from 'fs';
import path from 'path';

const LOG_DIR = path.join(process.cwd(), 'logs');
const LOG_FILE = path.join(LOG_DIR, 'app.log');

// Asegurar que el directorio de logs exista
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR);
}

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

class Logger {
    private formatMessage(level: LogLevel, source: string, message: string, data?: any) {
        const timestamp = new Date().toISOString();
        const dataStr = data ? ` | Data: ${JSON.stringify(data)}` : '';
        return `[${timestamp}] [${level.toUpperCase()}] [${source}] ${message}${dataStr}`;
    }

    private log(level: LogLevel, source: string, message: string, data?: any) {
        const formatted = this.formatMessage(level, source, message, data);

        // Console output for dev/prod logs
        if (level === 'error') {
            console.error(formatted);
        } else if (level === 'warn') {
            console.warn(formatted);
        } else {
            console.log(formatted);
        }

        // Persistir en archivo
        try {
            fs.appendFileSync(LOG_FILE, formatted + '\n');
        } catch (err) {
            console.error('❌ Falló la escritura en app.log:', err);
        }
    }

    info(source: string, message: string, data?: any) {
        this.log('info', source, message, data);
    }

    warn(source: string, message: string, data?: any) {
        this.log('warn', source, message, data);
    }

    error(source: string, message: string, data?: any) {
        this.log('error', source, message, data);
    }

    debug(source: string, message: string, data?: any) {
        this.log('debug', source, message, data);
    }
}

export const logger = new Logger();
