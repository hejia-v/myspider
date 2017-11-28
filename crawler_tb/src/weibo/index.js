import fs from 'fs'
import fse from 'fs-extra'
import path from 'path'
import request from 'request'
import cheerio from 'cheerio'
import jquery from 'jquery'
import winston from 'winston'
import FileCookieStore from 'tough-cookie-filestore'
import { requestEx, partition, rpartition, unicode2str, docDefaultView, query2dict } from '../utility'
import { genCookieJar, init } from '../cookies_mgr';

const $ = cheerio
const FAVHOME = 'http://weibo.com/fav?leftnav=1'
const USER_AGENT = 'Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'

// weibo.cookie需要定期更新
const cookiejar = genCookieJar('./__cookies/weibo.cookie', './__cookies/weibo.cookie.json', FAVHOME)

const options = {
    url: '',
    jar: cookiejar,
    headers: {
        'User-Agent': USER_AGENT,
    }
}

class FM {
    static view(data) {
        return data
    }
}

async function checkWeiboLogin(body) {
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

function getFavoriteslistHtml(body) {
    let html = ''
    $('script', body).each(function (i, elem) {
        const script = $(elem).html().trim()

        if (script.startsWith('FM.view')) {
            const scriptStr = `
                (function () {
                    ${FM.toString()}
                    return ${script}
                }())
            `
            const viewData = eval(scriptStr)
            if (viewData.domid == 'v6_pl_content_myfavoriteslist') {
                console.log(viewData.domid);
                fse.outputFileSync(`tmp/tmp.data.${i}.json`, JSON.stringify(viewData, null, 4))
                fse.outputFileSync(`tmp/tmp.data.${i}.html`, viewData.html)
                html = viewData.html
            }
        }
    })
    return html
}

function getFavPageNum(body) {
    const html = getFavoriteslistHtml(body)
    const pageNumStr = $('div > div > div:last-child > div > span > div > ul > li:first-child', html).text().trim()
    const pageNum = parseInt(pageNumStr.slice(1, -1))
    return pageNum
}

async function fetchWeiboFavPage(pageUrl) {
    const { response: res, body: body } = await requestEx(Object.assign({}, options, { url: FAVHOME }))
    if (res.statusCode != 200) {
        throw new Error(`error occurred when fetch ${this.url}, statusCode: ${res.statusCode}`)
    }
    const html = getFavoriteslistHtml(body)
    const window = await docDefaultView(html)
    const $ = jquery(window)
    const feed_list = []
    $("div[node-type='favContent'] > div > div:not(:last-child)").each((index, element) => {
            const jqImg = $('div.WB_feed_detail > div.WB_face.W_fl > div > a > img', element)
            const jqAuthor = $('div.WB_detail > div.WB_info > a', element)
            const jqWBFrom = $('div.WB_detail > div.WB_from > a:first-child', element)
            const jqWBText = $("div.WB_detail > div.WB_text[node-type='feed_list_content']", element)
            const jqWBTextFull = $("div.WB_detail > div.WB_text[node-type='feed_list_content_full']", element)  // 没有点击“展开全文”，并没有这一项，需要到feed_url去获取

            const jqComment = $("div.WB_feed_handle span[node-type='comment_btn_text']", element)
            const comment_text = jqComment.text().replace('', '').trim()
            const comment_num = comment_text == '评论' ? 0 : parseInt(comment_text)

            const feed_data = {
                uid: query2dict(jqImg.attr('usercard')).id,
                avater: jqImg.attr('src'),
                mid: $(element).attr('mid'),
                nickname: jqAuthor.attr('nick-name'),
                author_url: jqAuthor.attr('href'),
                feed_url: jqWBFrom.attr('href'),
                time: jqWBFrom.attr('title'),
                time_text: jqWBFrom.text().trim(),
                content: jqWBTextFull.prop("outerHTML") || jqWBText.prop("outerHTML"),
                media: '',
                comment_num: comment_num,
            }
            feed_list.push(feed_data)
        })
        console.log(feed_list)
    // todo: update content&media
}


async function fetchWeiboFav() {
    // winston.info('fetch tiezi: %s', this.url)
    const { response: res, body: body } = await requestEx(Object.assign({}, options, { url: FAVHOME }))
    if (res.statusCode != 200) {
        throw new Error(`error occurred when fetch ${this.url}, statusCode: ${res.statusCode}`)
    }
    await checkWeiboLogin(body)

    const pageNum = getFavPageNum(body)

    for (var i = 1; i < pageNum + 1; i++) {
        const pageUrl = `http://weibo.com/fav?pids=Pl_Content_MyFavoritesList&page=${i}&`
        console.log(pageUrl);
        await fetchWeiboFavPage(pageUrl)
        return
    }
    console.log(pageNum, '==============');
}


fetchWeiboFav().then(
    v => console.log('success!'),
    e => console.log(e)
)
