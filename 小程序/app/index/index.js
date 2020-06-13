const s = '使用说明：\n\
\n\
1. 输入汉字、拼音、拼音字头后返回通讯录检索结果，多个关键词用空格隔开；\n\
2. 不支持多音字、不支持拼音字头和拼音混输，混输关键词用空格隔开；\n\
3. 联系作者：QQ11313213\n\
'

var base64 = require('../lib/base64.js');
var pako = require('../lib/pako.js');
var data = require('../lib/data.js');

function zip(str) {
  var binaryString = pako.deflate(str, {to: 'string'});
  return base64.btoa(binaryString); // TODO: btoa is not defined
}
console.log(zip("hello lsx!"))

function unzip(b64Data) {
  var data = ''
  var strData = base64.atob(b64Data);
  data = pako.inflate(strData, {to: 'string'});
  return data;
}
console.log(unzip('eJzLSM3JyVfIKa5QBAAVTwOt'))

function init(s) {
  var data = s.split("\n");
  console.log("loading items:", data.length);
  //document.getElementById("contact").innerHTML = data.slice(0, 7).join("<br>");
  var ss = [];
  var i, line;
  for (i = 0; i < data.length; i++) { // i=9:使用说明和检索列表分离，且只有首次
    line = data[i].split(";");
    ss.push([line[0], data[i]]);
  }
  return ss;
}

function findName(ss, keys) {
  var ss_new = [];
  var i, j;
  if (keys.length == 1 && keys[0] == "") {
    for (i = 0; i < 3; i++) {
      ss_new.push(ss[i][0])
    }
    return ss_new;
  }
  for (i = 3; i < ss.length; i++) {
    if (ss_new.length == 100)
      break;
    var s = ss[i];
    var ok = 1;
    for (j = 0; j < keys.length; j++) {
      var key = keys[j];
      if (s[1].indexOf(key) == -1) {
        ok = 0
      }
    }
    if (ok) {
      ss_new.push(s[0])
    }
  }
  if (ss_new.length == 0) {
    ss_new.push("未找到匹配的结果。")
  }
  return ss_new;
}

const ss = init(unzip(data.s));

Page({
  data: {
    //inputValue: '',
    items: []
  },
  bindKeyInput: function (e) {
    var keys = e.detail.value.toLowerCase().split(" ");
    //var result = "查找结果：\n" + findName(ss, keys).join("\n") + "\n";
    var result_arr = findName(ss, keys);
    this.setData({
      items: result_arr
    })
  }
})
