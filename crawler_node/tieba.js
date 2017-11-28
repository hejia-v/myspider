const https = require('https')
const _url = require('url')
const fs = require('fs')
const request = require('request')
const async = require('async')
const cheerio = require('cheerio')


const TOKEN_URL = 'https://passport.baidu.com/v2/api/?getapi&tpl=mn&apiver=v3'
const INDEX_URL = 'https://www.baidu.com/'
const LOGIN_URL = 'https://passport.baidu.com/v2/api/?login'
const VERIFY_URL = 'http://tieba.baidu.com/f/user/json_userinfo'
const CANCER_STORETHREAD_URL = 'http://tieba.baidu.com/i/submit/cancel_storethread'

const USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'

const LOGIN_DATA = {
    "staticpage": "https://passport.baidu.com/static/passpc-account/html/V3Jump.html",
    "token": "",
    "tpl": "mn",                               // 重要,需要跟TOKEN_URL中的相同
    "username": "",
    "password": "",
}

const cookiejar = request.jar()


function initial(callback) {
    request({url: INDEX_URL, jar: cookiejar}, function (error, response, body) {
        console.log('initial...')
        callback(null)
    })
}


function getToken(callback) {
    let options = {
        url: TOKEN_URL,
        jar: cookiejar,
        headers: {
            'User-Agent': USER_AGENT,
        }
    }

    request(options, function (error, response, body) {
        if (!error && response.statusCode == 200) {
            console.log('get token...')

            let m = body.match(/"token" : "([^"]+?)",/)
            if (m) {
                token = m[1]
                console.log('token: ', token)
                callback(null, token)
            }
        }
    })
}


function login (username, password, token, callback) {
    let loginData = Object.assign({}, LOGIN_DATA, 
    {username: String(username), password: String(password), token})

    console.log(loginData)

    let options = {
        url: LOGIN_URL,
        jar: cookiejar,
        headers: {
            'User-Agent': USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip,deflate,sdch",
            "Accept-Language": "en-US,en;q=0.8,zh;q=0.6",
            "Host": "passport.baidu.com",
            "Origin": "http://www.baidu.com",
            "Referer": "http://www.baidu.com/",
        },
        form: loginData,
    }

    // 有验证码的时候会挂
    
    request.post(options, function (error, response, body) {
        if (!error && response.statusCode == 200) {
            console.log('login...')
            callback(null)
        }
    })
}


function verifyLogin(callback) {
    let options = {
        url: VERIFY_URL,
        jar: cookiejar,
        headers: {
            'User-Agent': USER_AGENT,
        }
    }

    request(options, function (error, response, body) {
        if (!error && response.statusCode == 200) {
            let jsonObj = JSON.parse(body)
            if (jsonObj.no == 0) {
                console.log('OK, login succes')
                callback(null)
            } else {
                callback('WTF, there is something wrong...')
            }
        }
    })
}


function getFavors(username, callback) {
    let url = encodeURI(`http://tieba.baidu.com//i/sys/jump?un=${username}&type=storethread`)
    let $ = cheerio
    let favthItemList = []
    let count = 1

    function fetchFavorPage(url) {
        let options = {
            url: url,
            jar: cookiejar,
            headers: {
                'User-Agent': USER_AGENT,
            }
        }

        console.log(`第${count++}页：${url}`)

        request(options, function (error, response, body) {
            if (!error && response.statusCode == 200) {

                $('#feed ul li', body).each(function(i, elem) {
                    let item = {
                        title: $('.favth_item_title', elem).text().trim(),
                        forum: $('.favth_item_forum', elem).text().trim(),
                        author: $('.favth_item_author', elem).text().trim(),
                        status: $('.j_favth_status', elem).text().trim(),
                        url: $('.favth_item_title a', elem).attr('href').trim(),
                    }

                    favthItemList.push(item)
                })

                let nextUrls = $('#pager a', body).filter(function(i, elem) {
                    return $(elem).text().trim().includes('下一页')
                })

                if (nextUrls.length >= 1) {
                    let nextUrl = nextUrls.get(0).attribs.href.trim()
                    nextUrl = 'http://tieba.baidu.com' + nextUrl
                    fetchFavorPage(nextUrl)
                } else {
                    fs.writeFileSync('./tieba-favors.json', JSON.stringify(favthItemList, null, 4))
                    callback(null)
                }
            }
        })
    }

    fetchFavorPage(url)
}


function getItbTbs(callback) {
    let options = {
        url: 'http://tieba.baidu.com/',
        jar: cookiejar,
        headers: {
            'User-Agent': USER_AGENT,
        }
    }

    request(options, function (error, response, body) {
        if (!error && response.statusCode == 200) {
            let m = body.match(/PageData.itbtbs = "([^"]+?)"/)
            if (m) {
                itbtbs = m[1]
                console.log('itbtbs: ', itbtbs)
                callback(null, itbtbs)
            }
        }
    })
}


function cancerFavors(itbtbs, callback) {
    let data = fs.existsSync('./tieba-favors.json') ?
    JSON.parse(fs.readFileSync('./tieba-favors.json')) : []
    let count = 1

    function getNextTid() {
        while (data.length > 0) {
            let item = data.pop()
            return item.url.slice(3)
        }
        return null
    }

    function cancerStoreThread(tid) {
        let options = {
            url: CANCER_STORETHREAD_URL,
            jar: cookiejar,
            headers: {
                'User-Agent': USER_AGENT, 
                'Host' : 'tieba.baidu.com', 
                'Origin' : 'http://tieba.baidu.com', 
                'Referer' : `http://tieba.baidu.com/p/${tid}`, 
            },  
            form: {
                tbs: itbtbs,
                tid: tid,
                type: 0,
                datatype: 'json',
                ie: 'utf-8'
            },
        }

        console.log(`${count++}：http://tieba.baidu.com/p/${tid}`)

        request.post(options, function (error, response, body) {
            if (!error && response.statusCode == 200) {
                console.log(body)

                let nextTid = getNextTid()
                if (nextTid) {
                    cancerStoreThread(nextTid)
                } else {
                    callback(null)
                }
            }
        })
    }

    let tid = getNextTid()
    if (tid) {
        cancerStoreThread(tid)
    }
}



(function test() {

    let data = fs.existsSync('./user.json') ? JSON.parse(fs.readFileSync('./user.json')) : {}
    let {username, password} = data
    if (!username || !password) {
        console.log("read user.json failed!")
        return
    }

    console.time("waterfall方法");

    async.waterfall([
        initial,
        getToken,
        login.bind(null, username, password),
        verifyLogin,
        getFavors.bind(null, username),
        getItbTbs,
        cancerFavors,
    ], function(err, result){

        if (err) {
            console.log(err);
        }

        console.timeEnd("waterfall方法");
    })

}())

