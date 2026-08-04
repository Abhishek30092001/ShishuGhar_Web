const https = require('https');

https.get('https://bharatlas.com/view/lgd_blocks', (res) => {
    let data = '';
    res.on('data', (chunk) => {
        data += chunk;
        if (data.length > 500000) { // get enough to see properties
            res.destroy();
            try {
                // Find first occurrence of "properties"
                let propIdx = data.indexOf('"properties"');
                let endIdx = data.indexOf('}', propIdx);
                console.log(data.substring(propIdx, endIdx + 1));
            } catch (e) {
                console.log(e);
            }
        }
    });
}).on('error', (e) => {
    console.error(e);
});
