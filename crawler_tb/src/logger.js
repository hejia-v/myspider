import os from 'os'
import path from 'path'
import fse from 'fs-extra'
import moment from 'moment'
import stackTrace from 'stack-trace'
import winston from 'winston'
import DailyRotateFile from 'winston-daily-rotate-file'

const logDir = path.join(process.cwd(), 'log')
fse.mkdirsSync(logDir)

const dateFormat = () => moment().format('YYYY-MM-DD HH:mm:ss:SSS')

const allLoggerTransport = new DailyRotateFile({
    name: 'all',
    filename: path.join(logDir, `crawler.all@${os.hostname()}.log`),
    timestamp: dateFormat,
    level: 'info',
    colorize: true,
    maxsize: 1024 * 1024 * 10,
    datePattern: '.yyyy-MM-dd'
})

const consoleTransport = new(winston.transports.Console)({
    name: 'console',
    timestamp: dateFormat,
    level: 'debug',
    colorize: true,
    datePattern: '.yyyy-MM-dd'
})

const errorTransport = new(winston.transports.File)({
    name: 'error',
    filename: path.join(logDir, `crawler.error@${os.hostname()}.log`),
    timestamp: dateFormat,
    level: 'error',
    colorize: true
})

// 日志
const logger = new(winston.Logger)({
    transports: [
        consoleTransport,
        allLoggerTransport,
        errorTransport
    ]
})

// 崩溃日志
const crashLogger = new(winston.Logger)({
    transports: [
        new(winston.transports.File)({
            name: 'error',
            filename: path.join(logDir, `crawler.crash@${os.hostname()}.log`),
            level: 'error',
            handleExceptions: true,
            timestamp: dateFormat,
            humanReadableUnhandledException: true,
            json: false,
            colorize: true
        }),
        new(winston.transports.Console)({
            name: 'error.console',
            level: 'error',
            handleExceptions: true,
            timestamp: dateFormat,
            humanReadableUnhandledException: true,
            json: false,
            colorize: true
        })
    ]
})

// 数据库日志
const dbLoggerTransport = new(winston.transports.File)({
    name: 'db',
    filename: path.join(logDir, `crawler.db@${os.hostname()}.log`),
    timestamp: dateFormat,
    level: 'info'
})
logger.dbLogger = new(winston.Logger)({
    transports: [dbLoggerTransport]
})

logger.dbLogger.add(allLoggerTransport, {}, true)
logger.dbLogger.add(errorTransport, {}, true)


// 代理logger.error方法，加入文件路径和行号信息
let originalMethod = logger.error
logger.error = function () {
    let cellSite = stackTrace.get()[1]
    originalMethod.apply(logger, [arguments[0] + '\n', {
        filePath: cellSite.getFileName(),
        lineNumber: cellSite.getLineNumber()
    }])
}


export default {
    logger,
}

export {
    logger,
}
