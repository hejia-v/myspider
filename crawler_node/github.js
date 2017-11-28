const https = require('https')
const _url = require('url')
const fs = require('fs')
const request = require('request')
const async = require('async')


const USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'


function getStars(username, callback) {
    let link = `https://api.github.com/users/${username}/starred`
    let repoList = []

    function work(link) {
        let options = {
            host: 'api.github.com',  // 不要前面的https://
            path: _url.parse(link).path,
            url: link,
            headers: {
                'User-Agent': USER_AGENT,
            }
        }

        request.get(options, function (error, response, body) {
            if (!error && response.statusCode == 200) {
                let jsonObj = JSON.parse(body)
                let arr = jsonObj.map(
                    elem => ({name: elem.name, owner: elem.owner.login}))

                repoList = repoList.concat(arr)

                let links = response.headers['link']
                let next_link = null
                if (links) {
                    matchs = links.match(/<([^<>]+?)>; rel="next"/)
                    next_link = matchs ? matchs[1] : null
                }

                if (next_link) {
                    work(next_link)
                } else {
                    callback(null, repoList)
                }

                console.dir(next_link)
            }
        })
    }

    work(link)
}


function star(username, password, repoList, callback) {

    function work() {
        if (repoList.length <= 0) {
            callback(null)
        }

        let item = repoList.pop()
        let options = {
            method: 'PUT',
            url: `https://api.github.com/user/starred/${item.owner}/${item.name}`,
            headers: {
                'User-Agent': USER_AGENT,
                'Content-Length': 0,
            }, 
            auth: { 
                'user': username, 
                'pass': password, 
            }
        }

        request(options, function (error, response, body) {
            if (!error && response.statusCode == 204) {
                console.log(`star ${item.owner}/${item.name}`)
            }
            work()
        })
    }

    work()
}


function unstar(username, password, repoList, callback) {
    let total = repoList.length
    let count = 0

    for(let item of repoList) {
        let item = repoList.pop()
        let options = {
            method: 'DELETE',
            url: `https://api.github.com/user/starred/${item.owner}/${item.name}`,
            headers: {
                'User-Agent': USER_AGENT,
                'Content-Length': 0,
            }, 
            auth: { 
                'user': username, 
                'pass': password, 
            }
        }

        request(options, function (error, response, body) {
            if (!error && response.statusCode == 204) {
                console.log(`unstar ${item.owner}/${item.name}`)
            }
            count++
            if (count >= total) {
                callback(null)
            }
        })
    }
}



function save(filename, data, callback) {
    fs.writeFileSync(filename, JSON.stringify(data, null, 4))
    callback(null)
}


function bind(fn) {
  return function (...args) {
      return fn.bind(this, ...args)
  }
}


(function test() {

    let username = ''
    let password = ''

    let data = fs.existsSync('./starred.json') ? JSON.parse(fs.readFileSync('./starred.json')) : []

    console.time("waterfall方法");

    async.waterfall([
        // bind(getStars)(username),
        // bind(save)('starred.json'),
        // bind(star)(username, password, data),
        bind(unstar)(username, password, data),
    ], function(err, result){
        if (err) {
            console.log(err);
        }
        console.timeEnd("waterfall方法");
    })

}())