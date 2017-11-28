import request from 'request'
import parse5 from 'parse5'
import jsdom from 'jsdom'

const partition = function (str, sep) {
    // str & sep must be string
    const idx = str.indexOf(sep)
    if (idx < 0) {
        return [str, '', '']
    }
    const head = str.slice(0, idx)
    const tail = str.slice(idx + sep.length, str.length)
    return [head, sep, tail]
}

const rpartition = function (str, sep) {
    // str & sep must be string
    const idx = str.lastIndexOf(sep)
    if (idx < 0) {
        return ['', '', str]
    }
    const head = str.slice(0, idx)
    const tail = str.slice(idx + sep.length, str.length)
    return [head, sep, tail]
}

const normalizeString = function (x) {
    return x.toString().trim()
}

const unicode2str = function (str) {
    const content = `<!DOCTYPE html><html><head></head><body>${str}</body></html>`
    const document = parse5.parse(content)
    const result = parse5.serialize(document.childNodes[1].childNodes[1])
    return result
}

const query2dict = function (queryStr) {
    const result = {}
    queryStr.split('&').map((elem, index) => {
        const [k, _, v] = partition(elem, '=')
        result[k] = v
    })
    return result
}

const docDefaultView = function (html) {
    return new Promise((resolve, reject) => {
        jsdom.env(html, (errors, window) => {
            if (errors) reject(error)
            resolve(window)
        })
    })
}

class RangeIterator {
    constructor(start, stop) {
        this.value = start
        this.stop = stop
    }

    [Symbol.iterator]() {
        return this
    }

    next() {
        var value = this.value
        if (value < this.stop) {
            this.value++
            return { done: false, value: value }
        } else {
            return { done: true, value: undefined }
        }
    }
}

const range = function (start, stop) {
    return new RangeIterator(start, stop)
}

const print_v1 = function (str, title = '', linechar = '-', linelen = 80) {
    title = title.trim()
    let top = title.padStart(linelen / 2 + title.length / 2 - 1, linechar).padEnd(linelen - 2, linechar)
    top = top.replace(title, ` ${title} `).trim()
    console.log(top)
    console.log(str)
    console.log(''.padEnd(top.length, linechar))
}

const requestEx = function (options) {
    return new Promise(function (resolve, reject) {
        request(options, function (error, response, body) {
            if (error) reject(error)
            resolve({
                response,
                body
            })
        })
    })
}

export default {
    partition,
    rpartition,
    print_v1,
    normalizeString,
    unicode2str,
    requestEx,
    range,
    docDefaultView,
    query2dict,
}

export {
    partition,
    rpartition,
    print_v1,
    normalizeString,
    unicode2str,
    requestEx,
    range,
    docDefaultView,
    query2dict,
}
