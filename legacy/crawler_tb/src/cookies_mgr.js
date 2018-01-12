import fs from 'fs'
import fse from 'fs-extra'
import request from 'request'
import FileCookieStore from 'tough-cookie-filestore'
import { requestEx } from './utility'

const BAIDU_VERIFY_URL = 'http://tieba.baidu.com/f/user/json_userinfo'
const USER_AGENT = 'Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'


function genCookieJar(cookieTextPath, cookieJarPath, url) {
    if (!fs.existsSync(cookieJarPath)) {
        fse.outputFileSync(cookieJarPath, '')
    }
    const cookiejar = request.jar(new FileCookieStore(cookieJarPath))

    const buffer = fs.readFileSync(cookieTextPath)
    const cookie_str = buffer.toString()

    cookie_str.split(';').map((elem, index) => {
        var cookie = request.cookie(elem.trim())
        cookiejar.setCookie(cookie, url)
    })
    return cookiejar
}

async function loginWithCookie (cookieTextPath, cookieJarPath, url) {
    const cookiejar = genCookieJar(cookieTextPath, cookieJarPath, url)

    const options = {
        url: url,
        jar: cookiejar,
        headers: {
            'User-Agent': USER_AGENT,
        }
    }

    return await requestEx(Object.assign({}, options, { url: url }))
}

async function genBaiduCookie() {
    const { response: res, body: body } = await loginWithCookie('./__cookies/tieba.cookie',
                                                                  './__cookies/tieba.cookie.json',
                                                                  BAIDU_VERIFY_URL)
    if (res.statusCode != 200) {
        throw new Error('error occurred when verify baidu login, statusCode:' + res.statusCode)
    }
    const jsonObj = JSON.parse(body)
    if (jsonObj.no == 0) {
        console.log('ok, login baidu succes')
    } else {
        console.log('wtf, there is something wrong when login baidu...')
    }
}

async function genWeiboCookie() {
    const { response: res, body: body } = await loginWithCookie('./__cookies/weibo.cookie',
                                                                  './__cookies/weibo.cookie.json',
                                                                  'http://weibo.com/fav?leftnav=1')
    if (res.statusCode != 200) {
        throw new Error('error occurred when verify baidu login, statusCode:' + res.statusCode)
    }
    let cfg = `
        (function () {
            let $CONFIG = {}
            ${body.match(/\$CONFIG\[.+?;/g).join('\n\t')}
            return $CONFIG
        }())
    `
    cfg = eval(cfg)
    console.log(`微博昵称: ${cfg.nick}`)
}

async function init(name) {
    const funcMap = {
        'baidu': genBaiduCookie,
        'weibo': genWeiboCookie,
    }
    const func = funcMap[name]
    if (func) {
        await func()
    }
    return 'finished!'
}

// init('weibo').then(
//     v => console.log(v),
//     e => console.log(e)
// )

export default {
    genCookieJar,
    init,
}

export {
    genCookieJar,
    init,
}
