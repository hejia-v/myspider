import { TiebaCrawler } from './tieba';


var tiebaCrawler = new TiebaCrawler(url);
tiebaCrawler.fetchTiezi().then(
    v => console.log('success!'),
    e => console.log(e)
)
// console.log(tiebaCrawler.toString());