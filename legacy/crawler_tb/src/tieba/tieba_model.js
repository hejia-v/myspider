import fs from 'fs'
import winston from 'winston'
import {normalizeString, range} from '../utility'

// 帖子
class TiebaTiezi {
    constructor(tid, title = '', author = '', forum = '') {
        this.tid = normalizeString(tid)
        this.title = normalizeString(title)
        this.author = normalizeString(author)
        this.forum = normalizeString(forum)
        this.cells = []

        winston.debug(`TiebaTiezi: tid: ${this.tid}, title: ${this.title}, author: ${this.author}, forum: ${this.forum}`)
    }

    add_cell(cell) {
        // assert(cell instanceof TiebaCell)
        console.assert(cell instanceof TiebaCell)
        this.cells.push(cell)
    }

    cell_count() {
        return this.cells.length
    }

    // 已被删除的楼层
    get_deleted_cells() {
        const nums = this.cells.map(c => parseInt(c.get_field('post_no')))
        const max_num = Math.max(...nums)
        return [...range(1, max_num + 1)].filter(x => !nums.includes(x))
    }

    update(tzObj) {
        console.assert(tzObj instanceof TiebaTiezi)
    }

    serial() {
        let data = this.cells.map(c => c.serial())
        let tiezi_data = {
            'tid': this.tid,
            'title': this.title,
            'author': this.author,
            'forum': this.forum,
            'cells': data,
        }
        return tiezi_data
    }

    //  从origin_driver获取上一次的数据
    dump(driver, origin_driver) {
        // from driver.driver import TiebaDriver
        // assert(isinstance(driver, TiebaDriver))

        // tiezi_data = driver.get_tiezi_data(this.tid)
        // if tiezi_data:
        //     old_tiezi_obj = TiebaTiezi.create(tiezi_data)
        //     old_tiezi_obj.update(this)
        //     driver.save(old_tiezi_obj.serial())
        // else:
        //     driver.save(this.serial())
        fs.writeFileSync(`./test.${this.tid}.json`, JSON.stringify(this.serial(), null, 4))
    }

    static create(tiezi_data) {
        const tid = tiezi_data.tid
        const title = tiezi_data.title
        const author = tiezi_data.author
        const forum = tiezi_data.forum
        const cells = tiezi_data.cells

        const tzObj = TiebaTiezi(str(tid), str(title), str(author), str(forum))
        cells.forEach(cell_data => {
            cell_obj = TiebaCell.create(cell_data)
            tzObj.add_cell(cell_obj)
        })
        return tzObj
    }
}


// 帖子的楼层
class TiebaCell {
    constructor() {
        this.author_data = {}
        this.content_data = {}
        this.comments = [] // 楼中楼
        this.ext_data = {}
    }

    get_field(field, major) {
        switch (major) {
            case 'author':
                return this.author_data[field]
            case 'content':
                return this.content_data[field]
            case 'ext':
                return this.ext_data[field]
            default:
                for (let data of [this.author_data, this.content_data, this.ext_data]) {
                    if (field in data) {
                        return data[field]
                    }
                }
        }
        return null
    }

    update_author_data(author_data) {
        this.author_data = Object.assign({}, this.author_data, author_data)
    }

    update_content_data(content_data) {
        this.content_data = Object.assign({}, this.content_data, content_data)
    }

    update_comments(comment_list) {
        // todo: 合并的情况
        this.comments = comment_list
    }

    update_ext_data(ext_data) {
        this.ext_data = Object.assign({}, this.ext_data, ext_data)
    }

    serial() {
        const data = {
            author: this.author_data,
            content: this.content_data,
            comments: this.comments.map(c => c.serial()),
            ext: this.ext_data,
        }
        return data
    }

    static create(cell_data) {
        const cell_obj = new TiebaCell()
        const author_data = cell_data.author || {}
        const content_data = cell_data.content || {}
        const comments = cell_data.comments
        const ext_data = cell_data.ext || {}

        if (author_data)
            cell_obj.update_author_data(author_data)
        if (content_data)
            cell_obj.update_content_data(content_data)
        if (comments)
            cell_obj.update_comments(comments.map(d => new TiebaLZL.create(d)))
        if (ext_data)
            cell_obj.update_ext_data(ext_data)
        return cell_obj
    }
}


// 楼中楼
class TiebaLZL {
    constructor() {
        this.data = {}
    }

    update(lzl_data) {
        if (!lzl_data)
            return
        this.data = Object.assign({}, this.data, lzl_data)
    }

    serial() {
        return this.data
    }

    static create(lzl_data) {
        const lzl_obj = new TiebaLZL()
        lzl_obj.update(lzl_data)
        return lzl_obj
    }
}







export default {
    TiebaTiezi,
    TiebaCell,
    TiebaLZL,
}

export {
    TiebaTiezi,
    TiebaCell,
    TiebaLZL,
}
