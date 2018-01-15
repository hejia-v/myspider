import fs from 'fs'
import fse from 'fs-extra'

var args = process.argv.splice(2)
const [soptype, tmpfile] = [...args]
const optype = parseInt(soptype)

function output(text) {
    fse.outputFileSync(tmpfile, text)
}

function checkWeiboLogin(body) {
    let cfg = `
        (function () {
            let $CONFIG = {}
            ${body.match(/\$CONFIG\[.+?;/g).join('\n\t')}
            return $CONFIG
        }())
    `
    cfg = eval(cfg)
    return cfg
}

function main() {
    console.log(`args: ${args}`);
    console.log(`tmpfile: ${tmpfile}`);
    console.log(`optype: ${optype}`);

    const buffer = fs.readFileSync(tmpfile)
    const input = buffer.toString()
    output('')

    let o = checkWeiboLogin(input)
    output(JSON.stringify(o, null, 4))
}

main()
