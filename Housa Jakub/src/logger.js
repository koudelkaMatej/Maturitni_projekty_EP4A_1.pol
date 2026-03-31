const fs = require('fs');
const path = require('path');

const LOG_DIR = path.join(__dirname, '..', 'logs');

// Ensure logs directory exists
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
}

const streams = {
    combined: fs.createWriteStream(path.join(LOG_DIR, 'combined.log'), { flags: 'a' }),
    error:    fs.createWriteStream(path.join(LOG_DIR, 'error.log'),    { flags: 'a' }),
    orders:   fs.createWriteStream(path.join(LOG_DIR, 'orders.log'),   { flags: 'a' }),
};

const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
const MIN_LEVEL = LEVELS[process.env.LOG_LEVEL] ?? LEVELS.info;

function write(level, context, message, extra) {
    if (LEVELS[level] < MIN_LEVEL) return;

    const entry = {
        ts:  new Date().toISOString(),
        lvl: level.toUpperCase(),
        ctx: context,
        msg: message,
        ...(extra !== undefined ? { data: extra } : {}),
    };

    const line = JSON.stringify(entry) + '\n';

    // Always write to combined
    streams.combined.write(line);

    // Errors also go to error.log
    if (level === 'error') streams.error.write(line);

    // Order-related context goes to orders.log
    if (context === 'checkout' || context === 'order') streams.orders.write(line);

    // Console output (coloured for terminal readability)
    const colors = { debug: '\x1b[36m', info: '\x1b[32m', warn: '\x1b[33m', error: '\x1b[31m' };
    const reset = '\x1b[0m';
    const prefix = `${colors[level]}[${entry.lvl}]${reset} ${entry.ts} [${context}]`;
    const extraStr = extra !== undefined ? ' ' + JSON.stringify(extra) : '';
    console[level === 'warn' ? 'warn' : level === 'error' ? 'error' : 'log'](
        `${prefix} ${message}${extraStr}`
    );
}

const logger = {
    debug: (ctx, msg, data) => write('debug', ctx, msg, data),
    info:  (ctx, msg, data) => write('info',  ctx, msg, data),
    warn:  (ctx, msg, data) => write('warn',  ctx, msg, data),
    error: (ctx, msg, data) => write('error', ctx, msg, data),

    // Shortcut: create a child logger bound to a fixed context
    child: (context) => ({
        debug: (msg, data) => write('debug', context, msg, data),
        info:  (msg, data) => write('info',  context, msg, data),
        warn:  (msg, data) => write('warn',  context, msg, data),
        error: (msg, data) => write('error', context, msg, data),
    }),

    // Morgan stream — pipes HTTP access logs into combined.log
    morganStream: {
        write: (message) => {
            const line = JSON.stringify({
                ts:  new Date().toISOString(),
                lvl: 'HTTP',
                msg: message.trim(),
            }) + '\n';
            streams.combined.write(line);
        },
    },
};

module.exports = logger;
