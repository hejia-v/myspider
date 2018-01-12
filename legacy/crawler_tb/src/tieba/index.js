import fs from 'fs'
import fse from 'fs-extra'
import path from 'path'
import request from 'request'
import cheerio from 'cheerio'
import winston from 'winston'
import FileCookieStore from 'tough-cookie-filestore'
import { requestEx, partition, rpartition, unicode2str } from '../utility'
import TiebaModel from './tieba_model';

const TOKEN_URL = 'https://passport.baidu.com/v2/api/?getapi&tpl=mn&apiver=v3'
const INDEX_URL = 'https://www.baidu.com/'
const LOGIN_URL = 'https://passport.baidu.com/v2/api/?login'
const VERIFY_URL = 'http://tieba.baidu.com/f/user/json_userinfo'
const USER_AGENT = 'Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'

const cookiejar = request.jar(new FileCookieStore('./__cookies/tieba.cookie.json'))

const options = {
    url: VERIFY_URL,
    jar: cookiejar,
    headers: {
        'User-Agent': USER_AGENT,
    }
}


class TiebaCrawler {
    constructor(url, dump=true, backup=true) {
        let obj = this._getUrlAndTid(url)
        this.url = obj.url;
        this.tid = obj.tid;
        this.dump = dump;
        this.backup = backup;
        winston.debug('url: %s', this.url)
        winston.debug('tid: %s', this.tid)
    }

    _getUrlAndTid(url) {
        let [s, _, e] = rpartition(url, '?pn=')
        url = s || e;
        [s, _, e] = rpartition(url, '?see_lz=')
        url = s || e;

        [s, _, e] = partition(url, 'tieba.baidu.com/p/')
        let tid = e
        return { url, tid }
    }

    // 获取帖子内容
    async fetchTiezi() {
        let $ = cheerio

        winston.info('fetch tiezi: %s', this.url)

        const { response: res, body: body } = await requestEx(Object.assign({}, options, { url: this.url }))
        if (res.statusCode != 200) {
            throw new Error(`error occurred when fetch ${this.url}, statusCode: ${res.statusCode}`)
        }

        // 获取帖子总页数
        let pageCount = $('#thread_theme_5 > div.l_thread_info > ul > li:nth-child(2) > span:nth-child(2)', body).text()
        pageCount = parseInt(pageCount)
        winston.info("tid: %s, 共%s页", this.tid, pageCount)

        // 获取帖子基本信息
        let forum = $('#container div.card_top > div.card_title > a.card_title_fname', body).text()
        let title = $('#j_core_title_wrap > h3', body).attr('title')
        let data_field = $('#j_p_postlist > div:nth-child(1)', body)[0].attribs['data-field']
        data_field = JSON.parse(data_field)
        let author = data_field.author.user_name

        const tzObj = new TiebaModel.TiebaTiezi(this.tid, title, author, forum)

        // 获取每一页的内容
        for (let pageNum = 1; pageNum < pageCount + 1; pageNum++) {
            let pageUrl = `${this.url}?pn=${pageNum}`
            await this._fetch_tiezi_single_page(this.tid, pageUrl, tzObj)
        }
            tzObj.dump()
            return tzObj
    }

    // 获取单页帖子的内容
    async _fetch_tiezi_single_page(tid, pageUrl, tieziObj) {
        winston.debug('fetch tiezi page: %s', pageUrl)
        // assert(tieziObj instanceof TiebaModel.TiebaTiezi)
        console.assert(tieziObj instanceof TiebaModel.TiebaTiezi)

        let $ = cheerio
        const { response: res, body: body } = await requestEx(Object.assign({}, options, { url: pageUrl }))

        let lastCellCount = tieziObj.cell_count()
        let postList = $('#j_p_postlist > div', body)

        for (let i = 0; i < postList.length; i++) {
            let post = postList[i]

            if (this._check_is_ad_post(post)) {
                continue
            }

            let data_field = post.attribs['data-field']
            data_field = JSON.parse(data_field)

            // 创建楼层数据对象
            let cell = TiebaModel.TiebaCell.create(data_field)
            tieziObj.add_cell(cell)

            let badge_title = $('.d_badge_title', post).text()
            let badge_lv = $('.d_badge_lv', post).text()
            if (!badge_title || !badge_lv) {
                winston.error('解析用户等级贴吧出错: ' + $(post).text())
                continue
            }
            badge_lv = parseInt(badge_lv)
            let post_date = $('div.post-tail-wrap > span:last-child', post).text()

            let extdata = {
                badge_title,
                badge_lv,
                post_time: post_date
            }

            cell.update_ext_data(extdata);

            await this._fetch_lzl(cell)
            // console.log(extdata);
            // console.log();
        }
        winston.debug('currnet tiezi page cells: %s', tieziObj.cell_count() - lastCellCount)
    }

    _check_is_ad_post(postElem) {
        let $ = cheerio
        let attribs = postElem.attribs
        let data_field = attribs['data-field']
        if (!data_field) {
            return true
        }
        let core_reply = $('.core_reply', postElem).text().trim()
        if (core_reply == '广告') {
            return true
        }

        try {
            JSON.parse(data_field)
        } catch (e) {
            if (data_field.includes('{?=blockNum?}')) {
                winston.error('广告楼层，data-field中有{?=blockNum?}')
                return true
            }
            winston.error(e)
            return true
        }
        return false
    }

    // 获取楼中楼
    async _fetch_lzl(cell) {
        console.assert(cell instanceof TiebaModel.TiebaCell)
        let comment_num = cell.get_field('comment_num', 'content')

        if (!comment_num)
            return

        try {
            comment_num = parseInt(comment_num)
        } catch (e) {
            comment_num = 0
        }

        if (comment_num <= 0)
            return

        const pid = cell.get_field('post_id', 'content')
        let comment_url = `http://tieba.baidu.com/p/comment?tid=${this.tid}&pid=${pid}&pn=1`

        let $ = cheerio
        const { response: cmt_r, body: cmt_text } = await requestEx(Object.assign({}, options, { url: comment_url }))

        let cmt_tail = $('li.lzl_li_pager.j_lzl_l_p.lzl_li_pager_s > p > a:last-child', cmt_text)
        let cmtTotalPages = 1 // 楼中楼总页数
        if (cmt_tail.text().trim() == '尾页') {
            // todo: 优化获取楼中楼数量的方法
            cmtTotalPages = parseInt(cmt_tail[0].attribs.href.slice(1))
        }

        const comment_list = []

        for (var cmtPage = 1; cmtPage < cmtTotalPages + 1; cmtPage++) {
            const cmt_url = `http://tieba.baidu.com/p/comment?tid=${this.tid}&pid=${pid}&pn=${cmtPage}`
            winston.debug('fetch tiezi lzl: %s', cmt_url)
            const { response: cmt_r, body: cmt_text } = await requestEx(Object.assign({}, options, { url: cmt_url }))

            $('li.lzl_single_post.j_lzl_s_p', cmt_text).each((i, single_cmt) => {
                const cmt_data_field = JSON.parse(single_cmt.attribs['data-field'])
                const username = cmt_data_field.user_name
                const spid = cmt_data_field.spid
                const portrait = cmt_data_field.portrait
                const user_href = $('div > a', single_cmt)[0].attribs.href
                const lzl_content_main = $('div > span.lzl_content_main', single_cmt).html()
                const content = unicode2str(lzl_content_main)

                const lzl_time = $('div > div > span.lzl_time', single_cmt).text()
                const single_cmt_data = {
                    username: username,
                    spid: spid,
                    portrait: portrait,
                    user_href: user_href,
                    content: content,
                    lzl_time: lzl_time,
                }

                const lzl_obj = TiebaModel.TiebaLZL.create(single_cmt_data)
                comment_list.push(lzl_obj)
            })
        }

        if (comment_num != comment_list.length) {
            winston.error('楼中楼数量不匹配： %s, %s', comment_num, comment_list.length)
            winston.error(cmt_text)
        }

        cell.update_comments(comment_list)

        return 0
    }

    toString() {
        return '(' + this.url + ', ' + this.tid + ')';
    }
}



export default {
    TiebaCrawler,
}

export {
    TiebaCrawler,
}
