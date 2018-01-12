import chai from 'chai';
import { partition, rpartition } from '../src/utility';

let expect = chai.expect;

describe('partition测试', function () {
    it('[\'1234\', \'abc\', \'567abc89\'] == partition(\'1234abc567abc89\', \'abc\')', function () {
        var s = '1234abc567abc89'
        var [a, b, c] = partition(s, 'abc')
        expect(a).to.be.equal('1234');
        expect(b).to.be.equal('abc');
        expect(c).to.be.equal('567abc89');
    });
});

describe('rpartition测试', function () {
    it('[\'1234abc567\', \'abc\', \'89\'] == rpartition(\'1234abc567abc89\', \'abc\')', function () {
        var s = '1234abc567abc89'
        var [a, b, c] = rpartition(s, 'abc')
        expect(a).to.be.equal('1234abc567');
        expect(b).to.be.equal('abc');
        expect(c).to.be.equal('89');
    });
});
