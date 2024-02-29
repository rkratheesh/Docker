!function(e,n){for(var t in n)e[t]=n[t]}(exports,function(e){var n={};function t(r){if(n[r])return n[r].exports;var o=n[r]={i:r,l:!1,exports:{}};return e[r].call(o.exports,o,o.exports,t),o.l=!0,o.exports}return t.m=e,t.c=n,t.d=function(e,n,r){t.o(e,n)||Object.defineProperty(e,n,{enumerable:!0,get:r})},t.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},t.t=function(e,n){if(1&n&&(e=t(e)),8&n)return e;if(4&n&&"object"==typeof e&&e&&e.__esModule)return e;var r=Object.create(null);if(t.r(r),Object.defineProperty(r,"default",{enumerable:!0,value:e}),2&n&&"string"!=typeof e)for(var o in e)t.d(r,o,function(n){return e[n]}.bind(null,o));return r},t.n=function(e){var n=e&&e.__esModule?function(){return e.default}:function(){return e};return t.d(n,"a",n),n},t.o=function(e,n){return Object.prototype.hasOwnProperty.call(e,n)},t.p="",t(t.s=9)}([function(e,n,t){var r=t(11)(),o=t(3);e.exports={number:function(e,n){return isNaN(e)?n:e},quote:function(e,n){return e=String(e).replace(/\\/g,"\\\\").replace(/"/g,'"'),n?'\\"'+e+'\\"':'"'+e+'"'},extractFilename:function(e){var n=e.match(/^(.+?)((?::\d+){0,4})$/),t=n[2].split(":").slice(1);return{filename:n[1],line:parseInt(t[0]||0,10),column:parseInt(t[1]||0,10)}},fail:function(e){console.error(String(e).trimRight()),process.exit(2)},atHomeDir:function(e){return o.join(r,e)},any:function(e,n){return new Promise((function(t,r){Promise.all(e.map((function(e){return e&&"function"==typeof e.then?e.then(t,(function(){})):e}))).then((function(e){r(n)}),r)}))},append:function(e,n){return String(e).replace(/\s*$/,(e?" ":"")+n)},assign:function(e,n){for(var t in n)Object.prototype.hasOwnProperty.call(n,t)&&(e[t]=n[t]);return e}}},function(e,n,t){var r=t(6).exec,o=t(0).number,i=t(0).quote,c=t(0).extractFilename,a=t(0).append;function u(e,n,t){return new Promise((function(u,s){var p;p=function(e,n){var t=c(e),r=n.pattern||"",u={projectPath:process.env.PROJECT_PATH||process.PWD||process.cwd(),line:t.line+o(n.line,1),column:t.column+o(n.column,1)};return/\{filename\}/.test(r)||(r=a(r,"{filename}:{line}:{column}")),r.replace(new RegExp("\\{("+Object.keys(u).join("|")+")\\}","g"),(function(e,n){return u[n]})).replace(/\{filename\}(\S*)/,(function(e,r){return i(t.filename+r,n.escapeQuotes)}))}(n,t=t||{}),e=t.patternOnly?p:a(i(e),p),r(e,(function(e){e?s(e):u()}))}))}e.exports=u,e.exports.factory=function(e,n){return function(t){return u(e,t,n)}},e.exports.detectAndOpenFactory=function(e,n){return function(t){return e().then((function(e){u(e,t,n)}))}}},function(e,n,t){var r=t(14),o=t(0).any;function i(e,n,t,i){function c(n){return this(n,e,t)}return i=i[process.platform]||[],o([].concat(n.map(c,r.command),i.map(c,r.path)),"Not detected")}e.exports=i,e.exports.lazy=function(e,n,t,r){var o;return function(){return o||(o=i(e,n,t,r)),o}},e.exports.platformSupport=function(e,n,t){return function(){return-1!==e.indexOf(process.platform)?Promise.resolve(t):Promise.reject('"Open in '+n+'" does not implemented for your platform ('+process.platform+")")}}},function(e,n){e.exports=require("path")},function(e,n,t){var r,o=t(7),i=t(3),c=t(2).lazy,a={pattern:"{projectPath} --line {line} {filename}"},u=(r="c:/Program Files (x86)/JetBrains/",o.existsSync(r)?o.readdirSync(r).map((function(e){return i.join(r,e)})).filter((function(e){return o.statSync(e).isDirectory()})):[]);e.exports=function(e){var n=c(e.name,[],"",{darwin:["/Applications/"+e.appFolder+".app/Contents/MacOS/"+e.executable],win32:u.map((function(n){return n+"/bin/"+e.executable+".exe"}))}),r=t(1).detectAndOpenFactory(n,a);return{settings:a,detect:n,open:r}}},function(e,n,t){e.exports={atom:t(13),code:t(15),sublime:t(16),webstorm:t(17),phpstorm:t(18),idea14ce:t(19),vim:t(20),visualstudio:t(21),emacs:t(22)}},function(e,n){e.exports=require("child_process")},function(e,n){e.exports=require("fs")},function(e,n){e.exports=function(e){return n=function(e){return'tell application "Terminal" to do script "'+e+'"'}("cd {projectPath}; "+e),"osascript -e '"+n+"'";var n}},function(e,n,t){var r=t(10);n.configure=r.configure,n.editors=t(5)},function(e,n,t){var r=t(0).extractFilename,o=t(0).number,i=t(0).assign,c=t(5),a=t(1).factory;e.exports={configure:function(e,n){n=n||function(){};var t,u=o((e=e||{}).line,1),s=o(e.column,1),p=e.editor,l=e.cmd;if(l||p||(c.hasOwnProperty(process.env.OPEN_FILE)?p=process.env.OPEN_FILE:l=process.env.OPEN_FILE||process.env.VISUAL||process.env.EDITOR),!p||c.hasOwnProperty(p)){if(l){var f={};c.hasOwnProperty(p)&&i(f,c[p].settings),t=a(l,i(f,e))}else{if(!p)return void n("Editor is not specified");t=c[p].open}return{open:function(e){if(!e)return Promise.reject("File is not specified");var n=r(e);return t([n.filename,Math.max(n.line-u,0),Math.max(n.column-s,0)].join(":"))}}}n("Wrong value for `editor` option: "+p)}}},function(e,n,t){"use strict";var r=t(12);e.exports="function"==typeof r.homedir?r.homedir:function(){var e=process.env,n=e.HOME,t=e.LOGNAME||e.USER||e.LNAME||e.USERNAME;return"win32"===process.platform?e.USERPROFILE||e.HOMEDRIVE+e.HOMEPATH||n||null:"darwin"===process.platform?n||(t?"/Users/"+t:null):"linux"===process.platform?n||(0===process.getuid()?"/root":t?"/home/"+t:null):n||null}},function(e,n){e.exports=require("os")},function(e,n,t){var r=t(0).atHomeDir,o={pattern:"{filename}:{line}:{column}"},i=t(2).lazy("Atom Editor",["atom"],"-h",{darwin:["/Applications/Atom.app/Contents/Resources/app/atom.sh"],win32:[r("AppData/Local/atom/bin/atom.cmd")]}),c=t(1).detectAndOpenFactory(i,o);e.exports={settings:o,detect:i,open:c}},function(e,n,t){var r=t(6).exec,o=t(7);t(0).quote;e.exports={command:function(e,n,t){return t?new Promise((function(o,i){r(e+" "+t,(function(t,r){t||0!==r.indexOf(n)?i(t):o(e)}))})):Promise.reject("No args to check command: "+e)},path:function(e,n){return o.existsSync(e)?Promise.resolve(e):Promise.reject("Path does not exist: "+e)}}},function(e,n,t){var r=t(0).atHomeDir,o={pattern:"-r -g {filename}:{line}:{column}"},i=t(2).lazy("Visual Studio Code",["code"],"-h",{darwin:["/Applications/Visual Studio Code.app/Contents/MacOS/Electron"],win32:["C:/Program Files/Microsoft VS Code/bin/code.cmd","C:/Program Files (x86)/Microsoft VS Code/bin/code.cmd",r("AppData/Local/Code/bin/code.cmd")]}),c=t(1).detectAndOpenFactory(i,o);e.exports={settings:o,detect:i,open:c}},function(e,n,t){var r={pattern:"{filename}:{line}:{column}"},o=t(2).lazy("Sublime Text",["subl"],"-h",{darwin:["/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl"],win32:["C:/Program Files/Sublime Text/subl.exe","C:/Program Files/Sublime Text 2/subl.exe","C:/Program Files/Sublime Text 3/subl.exe","C:/Program Files (x86)/Sublime Text/subl.exe","C:/Program Files (x86)/Sublime Text 2/subl.exe","C:/Program Files (x86)/Sublime Text 3/subl.exe"]}),i=t(1).detectAndOpenFactory(o,r);e.exports={settings:r,detect:o,open:i}},function(e,n,t){var r=t(4);e.exports=r({name:"WebStorm IDE",appFolder:"WebStorm",executable:"webstorm"})},function(e,n,t){var r=t(4);e.exports=r({name:"PhpStorm IDE",appFolder:"PhpStorm",executable:"phpstorm"})},function(e,n,t){var r=t(4);e.exports=r({name:"IDEA 14 CE",appFolder:"IntelliJ IDEA 14 CE",executable:"idea"})},function(e,n,t){var r={patternOnly:!0,escapeQuotes:!0,pattern:t(8)('vim {filename} \\"+call cursor({line}, {column})\\"')},o=t(2).platformSupport(["darwin"],"vim"),i=t(1).detectAndOpenFactory(o,r);e.exports={settings:r,detect:o,open:i}},function(e,n,t){var r=t(3).resolve(__dirname,"visualstudio.vbs"),o={pattern:"{filename} {line} {column}"},i=t(2).platformSupport(["win32"],"Visual Studio",r),c=t(1).detectAndOpenFactory(i,o);e.exports={settings:o,detect:i,open:c}},function(e,n,t){var r={patternOnly:!0,escapeQuotes:!0,pattern:t(8)('emacs --no-splash \\"+{line}:{column}\\" {filename}')},o=t(2).platformSupport(["darwin"],"vim"),i=t(1).detectAndOpenFactory(o,r);e.exports={settings:r,detect:o,open:i}}]));