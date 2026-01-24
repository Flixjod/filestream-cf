// ---------- Insert Your Data ---------- //

const BOT_TOKEN = "BOT_TOKEN"; // Insert your bot token.
const BOT_WEBHOOK = "/endpoint"; // Let it be as it is.
const BOT_SECRET = "BOT_SECRET"; // Insert a powerful secret text.
const BOT_OWNER = 1008848605; // Insert your telegram account id.
const BOT_CHANNEL = -1002199235178; // Insert your channel id.
const SIA_SECRET = "SIA_SECRET"; // Insert a powerful secret text.
const PUBLIC_BOT = false; // Make your bot public?
const OWNER_USERNAME = "FLiX_LY"; // Insert your username.
const BOT_NAME = "FileStream Bot"; // Bot Name.




// ---------- Do Not Modify ---------- // 

const WHITE_METHODS = ["GET", "POST", "HEAD"];
const HEADERS_FILE = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"};
const HEADERS_ERRR = {'Access-Control-Allow-Origin': '*', 'content-type': 'application/json'};

// File size limits in bytes
const MAX_TELEGRAM_SIZE = 4 * 1024 * 1024 * 1024; // 4GB for Telegram/Inline
const MAX_STREAM_SIZE = 2 * 1024 * 1024 * 1024; // 2GB for direct stream/download
const CHUNK_SIZE = 1024 * 1024; // 1MB chunks for streaming

const ERROR_404 = {"ok":false,"error_code":404,"description":"Bad Request: missing /?file= parameter", "credit": "https://github.com/vauth/filestream-cf"};
const ERROR_405 = {"ok":false,"error_code":405,"description":"Bad Request: method not allowed"};
const ERROR_406 = {"ok":false,"error_code":406,"description":"Bad Request: file type invalid"};
const ERROR_407 = {"ok":false,"error_code":407,"description":"Bad Request: file hash invalid by atob"};
const ERROR_408 = {"ok":false,"error_code":408,"description":"Bad Request: mode not in [attachment, inline, stream]"};
const ERROR_409 = {"ok":false,"error_code":409,"description":"Bad Request: file size exceeds maximum allowed limit"};
const ERROR_410 = {"ok":false,"error_code":410,"description":"Bad Request: file size exceeds streaming limit (2GB max)"};

// ---------- Event Listener ---------- // 

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event))
});

async function handleRequest(event) {
    const url = new URL(event.request.url);
    const file = url.searchParams.get('file');
    const mode = url.searchParams.get('mode') || "attachment";
    
    if (url.pathname === BOT_WEBHOOK) {return Bot.handleWebhook(event)}
    if (url.pathname === '/registerWebhook') {return Bot.registerWebhook(event, url, BOT_WEBHOOK, BOT_SECRET)}
    if (url.pathname === '/unregisterWebhook') {return Bot.unregisterWebhook(event)}
    if (url.pathname === '/getMe') {return new Response(JSON.stringify(await Bot.getMe()), {headers: HEADERS_ERRR, status: 202})}
    
    // Only show Home Page if NO file is requested
    if (url.pathname === '/' && !file) {return new Response(await getHomePage(), {headers: {'Content-Type': 'text/html'}})}
    
    if (url.pathname === '/stream' && file) {return new Response(await getStreamPage(url, file), {headers: {'Content-Type': 'text/html'}})}

    if (!file) {return Raise(ERROR_404, 404);}
    if (!["attachment", "inline", "stream"].includes(mode)) {return Raise(ERROR_408, 404)}
    if (!WHITE_METHODS.includes(event.request.method)) {return Raise(ERROR_405, 405);}
    try {await Cryptic.deHash(file)} catch {return Raise(ERROR_407, 404)}

    const channel_id = BOT_CHANNEL;
    const file_id = await Cryptic.deHash(file);
    
    // Validate file size before retrieving
    const fileInfo = await getFileInfo(channel_id, file_id);
    if (fileInfo.error_code) {return await Raise(fileInfo, fileInfo.error_code)};
    
    const fSize = fileInfo.size;
    const fType = fileInfo.type;
    
    // Check size limits based on mode
    if (fSize > MAX_STREAM_SIZE && (mode === 'inline' || mode === 'attachment')) {
        return Raise(ERROR_410, 413);
    }
    
    const retrieve = await RetrieveFile(channel_id, file_id);
    if (retrieve.error_code) {return await Raise(retrieve, retrieve.error_code)};

    const rdata = retrieve[0]
    const rname = retrieve[1]
    const rsize = retrieve[2]
    const rtype = retrieve[3]

    // Handle range requests for streaming
    const range = event.request.headers.get('Range');
    if (range && (mode === 'inline' || mode === 'stream')) {
        return handleRangeRequest(rdata, rname, rsize, rtype, range);
    }

    return new Response(rdata, {
        status: 200, headers: {
            "Content-Disposition": `${mode === 'stream' ? 'inline' : mode}; filename=${rname}`,
            "Content-Length": rsize,
            "Content-Type": rtype,
            "Accept-Ranges": "bytes",
            ...HEADERS_FILE
        }
    });
}

// ---------- Helper: Markdown Sanitizer ---------- //
function escapeMarkdown(text) {
    if (!text) return 'Unknown File';
    return text.replace(/`/g, "'");
}


// ---------- Helper: File Size Formatter ---------- //
function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ---------- Get File Info ---------- //

async function getFileInfo(channel_id, message_id) {
    let data = await Bot.editMessage(channel_id, message_id, await UUID());
    if (data.error_code){return data}
    
    let fSize = 0;
    let fType = "";
    
    if (data.document){
        fSize = data.document.file_size;
        fType = data.document.mime_type;
    } else if (data.audio) {
        fSize = data.audio.file_size;
        fType = data.audio.mime_type;
    } else if (data.video) {
        fSize = data.video.file_size;
        fType = data.video.mime_type;
    } else if (data.photo) {
        const fLen = data.photo.length - 1;
        fSize = data.photo[fLen].file_size;
        fType = "image/jpeg";
    } else {
        return ERROR_406
    }
    
    return {size: fSize, type: fType};
}

// ---------- Retrieve File ---------- //

async function RetrieveFile(channel_id, message_id) {
    let  fID; let fName; let fType; let fSize; let fLen;
    let data = await Bot.editMessage(channel_id, message_id, await UUID());
    if (data.error_code){return data}
    
    if (data.document){
        fLen = data.document.length - 1
        fID = data.document.file_id;
        fName = data.document.file_name;
        fType = data.document.mime_type;
        fSize = data.document.file_size;
    } else if (data.audio) {
        fLen = data.audio.length - 1
        fID = data.audio.file_id;
        fName = data.audio.file_name;
        fType = data.audio.mime_type;
        fSize = data.audio.file_size;
    } else if (data.video) {
        fLen = data.video.length - 1
        fID = data.video.file_id;
        fName = data.video.file_name;
        fType = data.video.mime_type;
        fSize = data.video.file_size;
    } else if (data.photo) {
        fLen = data.photo.length - 1
        fID = data.photo[fLen].file_id;
        fName = data.photo[fLen].file_unique_id + '.jpg';
        fType = "image/jpg";
        fSize = data.photo[fLen].file_size;
    } else {
        return ERROR_406
    }

    const file = await Bot.getFile(fID)
    if (file.error_code){return file}

    return [await Bot.fetchFile(file.file_path), fName, fSize, fType];
}

// ---------- Raise Error ---------- //

async function Raise(json_error, status_code) {
    return new Response(JSON.stringify(json_error), { headers: HEADERS_ERRR, status: status_code });
}

// ---------- Range Request Handler ---------- //

function handleRangeRequest(data, name, size, type, rangeHeader) {
    try {
        const parts = rangeHeader.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10) || 0;
        const end = parts[1] ? parseInt(parts[1], 10) : Math.min(start + CHUNK_SIZE - 1, size - 1);
        
        if (start >= size || end >= size || start > end) {
            return new Response(JSON.stringify({
                ok: false, error_code: 416, description: "Range Not Satisfiable"
            }), { status: 416, headers: { "Content-Range": `bytes */${size}`, ...HEADERS_ERRR } });
        }
        
        const chunksize = (end - start) + 1;
        const buffer = new Uint8Array(data);
        const chunk = buffer.slice(start, end + 1);
        
        return new Response(chunk, {
            status: 206,
            headers: {
                "Content-Range": `bytes ${start}-${end}/${size}`,
                "Accept-Ranges": "bytes",
                "Content-Length": chunksize.toString(),
                "Content-Type": type,
                "Cache-Control": "public, max-age=86400",
                ...HEADERS_FILE
            }
        });
    } catch (error) {
        return new Response(JSON.stringify({ok: false, error_code: 500, description: "Internal Server Error"}), {status: 500, headers: HEADERS_ERRR});
    }
}

// ---------- Stream Page Generator ---------- //

async function getStreamPage(url, fileHash) {
    const bot = await Bot.getMe();
    const streamUrl = `${url.origin}/?file=${fileHash}&mode=inline`;
    const downloadUrl = `${url.origin}/?file=${fileHash}`;
    const telegramUrl = `https://t.me/${bot.username}/?start=${fileHash}`;
     
    let fileName = 'Media File';
    let fileType = 'video';
    try {
        const channel_id = BOT_CHANNEL;
        const file_id = await Cryptic.deHash(fileHash);
        const data = await Bot.editMessage(channel_id, file_id, await UUID());
         
        if (data.document) {
            fileName = data.document.file_name;
            fileType = data.document.mime_type.startsWith('video') ? 'video' : 
                      data.document.mime_type.startsWith('audio') ? 'audio' : 'document';
        } else if (data.video) {
            fileName = data.video.file_name || 'Video File';
            fileType = 'video';
        } else if (data.audio) {
            fileName = data.audio.file_name || 'Audio File';
            fileType = 'audio';
        }
    } catch (e) {}
     
    const vlcUrl = `vlc://${streamUrl.replace('https://', '').replace('http://', '')}`;
    const mxUrl = `intent:${streamUrl}#Intent;package=com.mxtech.videoplayer.ad;end`;
     
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${fileName} - ${BOT_NAME}</title>
    <link rel="icon" type="image/png" href="https://i.ibb.co/pQ0tSCj/1232b12e0a0c.png">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .glass { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); }
        video, audio { max-width: 100%; border-radius: 12px; box-shadow: 0 20px 50px rgba(0,0,0,0.3); }
        .btn { transition: all 0.3s ease; transform: translateY(0); }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .copy-btn { cursor: pointer; }
        .copied { background: #10b981 !important; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .fade-in { animation: fadeIn 0.6s ease-out; }
    </style>
</head>
<body class="gradient-bg min-h-screen py-8 px-4">
    <div class="max-w-5xl mx-auto fade-in">
        <div class="glass rounded-2xl p-8 mb-6">
            <div class="text-center mb-6">
                <h1 class="text-4xl font-bold text-white mb-2">${BOT_NAME}</h1>
                <p class="text-purple-200">Premium File Streaming Service</p>
            </div>
             
            <div class="bg-white bg-opacity-10 rounded-xl p-6 mb-6">
                <h2 class="text-2xl font-semibold text-white mb-4">
                    <i class="fas fa-file-${fileType === 'video' ? 'video' : fileType === 'audio' ? 'audio' : 'alt'} mr-2"></i>
                    ${fileName}
                </h2>
                 
                ${fileType === 'video' ? `
                <div class="mb-6">
                    <video id="videoPlayer" controls preload="metadata" class="w-full">
                        <source src="${streamUrl}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>` : fileType === 'audio' ? `
                <div class="mb-6">
                    <audio controls preload="metadata" class="w-full">
                        <source src="${streamUrl}" type="audio/mpeg">
                        Your browser does not support the audio tag.
                    </audio>
                </div>` : ''}
                 
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <a href="${downloadUrl}" class="btn bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg text-center font-semibold">
                        <i class="fas fa-download mr-2"></i>Download File
                    </a>
                    <button onclick="copyToClipboard('${streamUrl}', this)" class="btn copy-btn bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold">
                        <i class="fas fa-copy mr-2"></i>Copy Link
                    </button>
                    ${fileType === 'video' ? `
                    <a href="${vlcUrl}" class="btn bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg text-center font-semibold">
                        <i class="fas fa-play-circle mr-2"></i>Play in VLC
                    </a>
                    <a href="${mxUrl}" class="btn bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg text-center font-semibold">
                        <i class="fas fa-play mr-2"></i>Play in MX Player
                    </a>` : ''}
                    <a href="${telegramUrl}" class="btn bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg text-center font-semibold">
                        <i class="fab fa-telegram mr-2"></i>Open in Telegram
                    </a>
                    <button onclick="shareFile()" class="btn bg-pink-600 hover:bg-pink-700 text-white px-6 py-3 rounded-lg font-semibold">
                        <i class="fas fa-share-alt mr-2"></i>Share
                    </button>
                </div>
            </div>
             
            <div class="bg-white bg-opacity-10 rounded-xl p-4 mb-6">
                <h3 class="text-lg font-semibold text-white mb-3"><i class="fas fa-link mr-2"></i>Direct Stream Link</h3>
                <div class="flex gap-2">
                    <input type="text" value="${streamUrl}" readonly class="flex-1 bg-gray-900 bg-opacity-50 text-white px-4 py-2 rounded-lg" id="streamLink">
                    <button onclick="copyToClipboard('${streamUrl}', this)" class="btn copy-btn bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>
             
            <div class="text-center">
                <p class="text-purple-200 text-sm">
                    <i class="fas fa-crown mr-1"></i>
                    Created by <a href="https://t.me/${OWNER_USERNAME}" class="text-yellow-300 hover:text-yellow-200 font-semibold" target="_blank">@${OWNER_USERNAME}</a>
                </p>
                <p class="text-purple-300 text-xs mt-2">Powered by ${BOT_NAME} on Cloudflare Workers</p>
            </div>
        </div>
    </div>
     
    <script>
        function copyToClipboard(text, btn) {
            navigator.clipboard.writeText(text).then(() => {
                const originalHTML = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check mr-2"></i>Copied!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.classList.remove('copied');
                }, 2000);
            });
        }
         
        function shareFile() {
            if (navigator.share) {
                navigator.share({
                    title: '${fileName}',
                    text: 'Check out this file from ${BOT_NAME}',
                    url: window.location.href
                }).catch(err => console.log('Error sharing:', err));
            } else {
                copyToClipboard(window.location.href, event.target);
            }
        }
    </script>
</body>
</html>`;
}

// ---------- Home Page Generator ---------- //

async function getHomePage() {
    const bot = await Bot.getMe();
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${BOT_NAME} - Premium File Streaming</title>
    <link rel="icon" type="image/png" href="https://i.ibb.co/pQ0tSCj/1232b12e0a0c.png">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .glass { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); }
        .feature-card { transition: all 0.3s ease; }
        .feature-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.3); }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
        .float { animation: float 3s ease-in-out infinite; }
    </style>
</head>
<body class="gradient-bg min-h-screen py-12 px-4">
    <div class="max-w-6xl mx-auto">
        <div class="text-center mb-12">
            <div class="float inline-block mb-6">
                <i class="fas fa-cloud-upload-alt text-white text-6xl"></i>
            </div>
            <h1 class="text-5xl md:text-6xl font-bold text-white mb-4">${BOT_NAME}</h1>
            <p class="text-xl text-purple-200 mb-6">Premium File Streaming & Download Service</p>
            <a href="https://t.me/${bot.username}" target="_blank" class="inline-block bg-white text-purple-600 px-8 py-3 rounded-full font-semibold text-lg hover:bg-purple-100 transition">
                <i class="fab fa-telegram mr-2"></i>Start Using Bot
            </a>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div class="glass feature-card rounded-xl p-6 text-center">
                <i class="fas fa-bolt text-yellow-300 text-4xl mb-4"></i>
                <h3 class="text-xl font-semibold text-white mb-2">Lightning Fast</h3>
                <p class="text-purple-200">Stream files instantly with Cloudflare's global CDN</p>
            </div>
            <div class="glass feature-card rounded-xl p-6 text-center">
                <i class="fas fa-shield-alt text-green-300 text-4xl mb-4"></i>
                <h3 class="text-xl font-semibold text-white mb-2">Secure & Private</h3>
                <p class="text-purple-200">Your files are encrypted and stored securely</p>
            </div>
            <div class="glass feature-card rounded-xl p-6 text-center">
                <i class="fas fa-mobile-alt text-blue-300 text-4xl mb-4"></i>
                <h3 class="text-xl font-semibold text-white mb-2">Multi-Platform</h3>
                <p class="text-purple-200">Stream on VLC, MX Player, or any device</p>
            </div>
        </div>
        
        <div class="glass rounded-2xl p-8 mb-8">
            <h2 class="text-3xl font-bold text-white mb-6 text-center">How It Works</h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="text-center">
                    <div class="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-3">1</div>
                    <p class="text-white font-semibold mb-2">Send File to Bot</p>
                    <p class="text-purple-200 text-sm">Upload any media file to the Telegram bot</p>
                </div>
                <div class="text-center">
                    <div class="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-3">2</div>
                    <p class="text-white font-semibold mb-2">Get Instant Link</p>
                    <p class="text-purple-200 text-sm">Receive streaming and download links</p>
                </div>
                <div class="text-center">
                    <div class="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-3">3</div>
                    <p class="text-white font-semibold mb-2">Stream Anywhere</p>
                    <p class="text-purple-200 text-sm">Play in browser, VLC, or MX Player</p>
                </div>
                <div class="text-center">
                    <div class="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-3">4</div>
                    <p class="text-white font-semibold mb-2">Share & Enjoy</p>
                    <p class="text-purple-200 text-sm">Share links with anyone, anytime</p>
                </div>
            </div>
        </div>
        
        <div class="text-center">
            <p class="text-purple-200 mb-2">
                <i class="fas fa-crown mr-1 text-yellow-300"></i>
                Created with ❤️ by <a href="https://t.me/${OWNER_USERNAME}" class="text-yellow-300 hover:text-yellow-200 font-semibold" target="_blank">@${OWNER_USERNAME}</a>
            </p>
            <p class="text-purple-300 text-sm">Powered by Cloudflare Workers</p>
        </div>
    </div>
</body>
</html>`;
}

// ---------- UUID Generator ---------- //

async function UUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// ---------- Hash Generator ---------- //

class Cryptic {
  static async getSalt(length = 16) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let salt = '';
    for (let i = 0; i < length; i++) {
        salt += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return salt;
  }

  static async getKey(salt, iterations = 1000, keyLength = 32) {
    const key = new Uint8Array(keyLength);
    for (let i = 0; i < keyLength; i++) {
        key[i] = (SIA_SECRET.charCodeAt(i % SIA_SECRET.length) + salt.charCodeAt(i % salt.length)) % 256;
    }
    for (let j = 0; j < iterations; j++) {
        for (let i = 0; i < keyLength; i++) {
            key[i] = (key[i] + SIA_SECRET.charCodeAt(i % SIA_SECRET.length) + salt.charCodeAt(i % salt.length)) % 256;
        }
    }
    return key;
  }

  static async baseEncode(input) {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    let output = '';
    let buffer = 0;
    let bitsLeft = 0;
    for (let i = 0; i < input.length; i++) {
        buffer = (buffer << 8) | input.charCodeAt(i);
        bitsLeft += 8;
        while (bitsLeft >= 5) {output += alphabet[(buffer >> (bitsLeft - 5)) & 31]; bitsLeft -= 5}
    }
    if (bitsLeft > 0) {output += alphabet[(buffer << (5 - bitsLeft)) & 31]}
    return output;
  }

  static async baseDecode(input) {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    const lookup = {};
    for (let i = 0; i < alphabet.length; i++) {lookup[alphabet[i]] = i}
    let buffer = 0;
    let bitsLeft = 0;
    let output = '';
    for (let i = 0; i < input.length; i++) {
        buffer = (buffer << 5) | lookup[input[i]];
        bitsLeft += 5;
        if (bitsLeft >= 8) {output += String.fromCharCode((buffer >> (bitsLeft - 8)) & 255); bitsLeft -= 8}
    }
    return output;
  }

  static async Hash(text) {
    const salt = await this.getSalt();
    const key = await this.getKey(salt);
    const encoded = String(text).split('').map((char, index) => {
        return String.fromCharCode(char.charCodeAt(0) ^ key[index % key.length]);
    }).join('');
    return await this.baseEncode(salt + encoded);
  }

  static async deHash(hashed) {
    const decoded = await this.baseDecode(hashed);
    const salt = decoded.substring(0, 16);
    const encoded = decoded.substring(16);
    const key = await this.getKey(salt);
    const text = encoded.split('').map((char, index) => {
        return String.fromCharCode(char.charCodeAt(0) ^ key[index % key.length]);
    }).join('');
    return text;
  }
}

// ---------- Telegram Bot ---------- //

class Bot {
  static async handleWebhook(event) {
    if (event.request.headers.get('X-Telegram-Bot-Api-Secret-Token') !== BOT_SECRET) {
      return new Response('Unauthorized', { status: 403 })
    }
    const update = await event.request.json()
    event.waitUntil(this.Update(event, update))
    return new Response('Ok')
  }

  static async registerWebhook(event, requestUrl, suffix, secret) {
    const webhookUrl = `${requestUrl.protocol}//${requestUrl.hostname}${suffix}`
    const response = await fetch(await this.apiUrl('setWebhook', { url: webhookUrl, secret_token: secret }))
    return new Response(JSON.stringify(await response.json()), {headers: HEADERS_ERRR})
  }

  static async unregisterWebhook(event) { 
    const response = await fetch(await this.apiUrl('setWebhook', { url: '' }))
    return new Response(JSON.stringify(await response.json()), {headers: HEADERS_ERRR})
  }

  static async getMe() {
    const response = await fetch(await this.apiUrl('getMe'))
    if (response.status == 200) {return (await response.json()).result;
    } else {return await response.json()}
  }

  static async sendMessage(chat_id, reply_id, text, reply_markup=[]) {
    const response = await fetch(await this.apiUrl('sendMessage', {chat_id: chat_id, reply_to_message_id: reply_id, parse_mode: 'markdown', text, reply_markup: JSON.stringify({inline_keyboard: reply_markup})}))
    if (response.status == 200) {return (await response.json()).result;
    } else {return await response.json()}
  }

  static async sendDocument(chat_id, file_id) {
    const response = await fetch(await this.apiUrl('sendDocument', {chat_id: chat_id, document: file_id}))
    if (response.status == 200) {return (await response.json()).result;
    } else {return await response.json()}
  }

  static async sendPhoto(chat_id, file_id) {
    const response = await fetch(await this.apiUrl('sendPhoto', {chat_id: chat_id, photo: file_id}))
    if (response.status == 200) {return (await response.json()).result;
    } else {return await response.json()}
  }
  
  static async copyMessage(chat_id, from_chat_id, message_id, reply_markup=[]) {
    const response = await fetch(await this.apiUrl('copyMessage', {
        chat_id: chat_id, 
        from_chat_id: from_chat_id, 
        message_id: message_id,
        reply_markup: JSON.stringify({inline_keyboard: reply_markup})
    }));
    if (response.status == 200) {return (await response.json()).result;
    } else {return await response.json()}
  }

  static async editMessage(channel_id, message_id, caption_text) {
      const response = await fetch(await this.apiUrl('editMessageCaption', {chat_id: channel_id, message_id: message_id, caption: caption_text}))
      if (response.status == 200) {return (await response.json()).result;
      } else {return await response.json()}
  }

  static async answerInlineArticle(query_id, title, description, text, reply_markup=[], id='1') {
    const data = [{type: 'article', id: id, title: title, thumbnail_url: "https://i.ibb.co/5s8hhND/dac5fa134448.png", description: description, input_message_content: {message_text: text, parse_mode: 'markdown'}, reply_markup: {inline_keyboard: reply_markup}}];
    const response = await fetch(await this.apiUrl('answerInlineQuery', {inline_query_id: query_id, results: JSON.stringify(data), cache_time: 1}))
    if (response.status == 200) {return (await response.json()).result;
    } else {return await response.json()}
  }

  static async answerInlineDocument(query_id, title, file_id, mime_type, reply_markup=[], id='1') {
    const data = [{type: 'document', id: id, title: title, document_file_id: file_id, mime_type: mime_type, description: mime_type, reply_markup: {inline_keyboard: reply_markup}}];
    const response = await fetch(await this.apiUrl('answerInlineQuery', {inline_query_id: query_id, results: JSON.stringify(data), cache_time: 1}))
    if (response.status == 200) {return (await response.json()).result;
    } else {return await response.json()}
  }

  static async answerInlinePhoto(query_id, title, photo_id, reply_markup=[], id='1') {
    const data = [{type: 'photo', id: id, title: title, photo_file_id: photo_id, reply_markup: {inline_keyboard: reply_markup}}];
    const response = await fetch(await this.apiUrl('answerInlineQuery', {inline_query_id: query_id, results: JSON.stringify(data), cache_time: 1}))
    if (response.status == 200) {return (await response.json()).result;
    } else {return await response.json()}
  }

  static async getFile(file_id) {
      const response = await fetch(await this.apiUrl('getFile', {file_id: file_id}))
      if (response.status == 200) {return (await response.json()).result;
      } else {return await response.json()}
  }

  static async fetchFile(file_path) {
      const file = await fetch(`https://api.telegram.org/file/bot${BOT_TOKEN}/${file_path}`);
      return await file.arrayBuffer()
  }

  static async apiUrl (methodName, params = null) {
      let query = ''
      if (params) {query = '?' + new URLSearchParams(params).toString()}
      return `https://api.telegram.org/bot${BOT_TOKEN}/${methodName}${query}`
  }

  static async Update(event, update) {
    if (update.inline_query) {await onInline(event, update.inline_query)}
    if ('message' in update) {await onMessage(event, update.message)}
  }
}

// ---------- Inline Listener ---------- // 

async function onInline(event, inline) {
  let  fID; let fName; let fType; let fSize; let fLen;

  if (!PUBLIC_BOT && inline.from.id != BOT_OWNER) {
    const buttons = [[{ text: "Source Code", url: "https://t.me/FLiX_LY" }]];
    return await Bot.answerInlineArticle(inline.id, "Access forbidden", "Deploy your own filestream-cf.", "*❌ ᴀᴄᴄᴇss ғᴏʀʙɪᴅᴅᴇɴ.*\n📡 Deploy your own [filestream-cf](https://github.com/vauth/filestream-cf) bot.", buttons)
  }
 
  try {await Cryptic.deHash(inline.query)} catch {
    const buttons = [[{ text: "Source Code", url: "https://github.com/vauth/filestream-cf" }]];
    return await Bot.answerInlineArticle(inline.id, "Error", ERROR_407.description, ERROR_407.description, buttons)
  }

  const channel_id = BOT_CHANNEL;
  const message_id = await Cryptic.deHash(inline.query);
  const data = await Bot.editMessage(channel_id, message_id, await UUID());

  if (data.error_code){
    const buttons = [[{ text: "Source Code", url: "https://t.me/FLiX_LY" }]];
    return await Bot.answerInlineArticle(inline.id, "Error", data.description, data.description, buttons)
  }

  if (data.document){
    fLen = data.document.length - 1
    fID = data.document.file_id;
    fName = data.document.file_name;
    fType = data.document.mime_type;
    fSize = data.document.file_size;
  } else if (data.audio) {
    fLen = data.audio.length - 1
    fID = data.audio.file_id;
    fName = data.audio.file_name;
    fType = data.audio.mime_type;
    fSize = data.audio.file_size;
  } else if (data.video) {
    fLen = data.video.length - 1
    fID = data.video.file_id;
    fName = data.video.file_name;
    fType = data.video.mime_type;
    fSize = data.video.file_size;
  } else if (data.photo) {
    fLen = data.photo.length - 1
    fID = data.photo[fLen].file_id;
    fName = data.photo[fLen].file_unique_id + '.jpg';
    fType = "image/jpg";
    fSize = data.photo[fLen].file_size;
  } else {
    return ERROR_406
  }

  if (fType == "image/jpg") {
    const buttons = [[{ text: "Send Again", switch_inline_query_current_chat: inline.query }]]
    return await Bot.answerInlinePhoto(inline.id, fName || "undefined", fID, buttons)
  } else {
    const buttons = [[{ text: "Send Again", switch_inline_query_current_chat: inline.query }]];
    return await Bot.answerInlineDocument(inline.id, fName || "undefined", fID, fType, buttons)
  }

}

// ---------- Message Listener ---------- // 

async function onMessage(event, message) {
    let fID; let fName; let fSave; let fType; let fSize = 0;
    let url = new URL(event.request.url);
    let bot = await Bot.getMe();

    // 1. Ignore messages from the bot itself
    if (message.via_bot && message.via_bot.username == bot.username) { return }

    // 2. Ignore messages from channels
    if (message.chat.id.toString().includes("-100")) { return }

    // 3. Handle Start Command
    if (message.text && (message.text === "/start" || message.text.startsWith("/start "))) {
        // Plain start
        if (message.text === "/start") {
             const buttons = [[{ text: "👨‍💻 Source Code", url: "https://t.me/FLiX_LY" }]];
             const startText = `👋 *ʜᴇʟʟᴏ ${message.from.first_name}*,\n\nI am a *ᴘʀᴇᴍɪᴜᴍ ғɪʟᴇ sᴛʀᴇᴀᴍ ʙᴏᴛ*.\n\n📂 *Send me any file* (Video, Audio, Document) and I will generate a direct download and streaming link for you.`;
             return Bot.sendMessage(message.chat.id, message.message_id, startText, buttons);
        }

        // Deep linking start
        const file = message.text.split("/start ")[1];
        if (!file) return; 

        try { await Cryptic.deHash(file) } catch { return await Bot.sendMessage(message.chat.id, message.message_id, ERROR_407.description) }

        const channel_id = BOT_CHANNEL;
        const message_id = await Cryptic.deHash(file);
        const data = await Bot.editMessage(channel_id, message_id, await UUID());

        if (data.document) {
            fID = data.document.file_id;
            return await Bot.sendDocument(message.chat.id, fID)
        } else if (data.audio) {
            fID = data.audio.file_id;
            return await Bot.sendDocument(message.chat.id, fID)
        } else if (data.video) {
            fID = data.video.file_id;
            return await Bot.sendDocument(message.chat.id, fID)
        } else if (data.photo) {
            fID = data.photo[data.photo.length - 1].file_id;
            return await Bot.sendPhoto(message.chat.id, fID)
        } else {
            return Bot.sendMessage(message.chat.id, message.message_id, "Bad Request: File not found")
        }
    }

    // 4. Access Control
    if (!PUBLIC_BOT && message.chat.id != BOT_OWNER) {
        const buttons = [[{ text: "Source Code", url: "https://t.me/FLiX_LY" }]];
        return Bot.sendMessage(message.chat.id, message.message_id, "*❌ ᴀᴄᴄᴇss ғᴏʀʙɪᴅᴅᴇɴ.*\n📡 Deploy your own [filestream-cf](https://t.me/FLiX_LY) bot.", buttons)
    }

    // 5. Detect File Type & Copy to Channel
    if (message.document || message.audio || message.video || message.photo) {
        
        // --- 5a. Extract Metadata ---
        if (message.document) {
            fName = message.document.file_name || "Document";
            fType = message.document.mime_type ? message.document.mime_type.split("/")[0] : "document";
            fSize = message.document.file_size;
        } else if (message.audio) {
            fName = message.audio.file_name || "Audio File";
            fType = message.audio.mime_type ? message.audio.mime_type.split("/")[0] : "audio";
            fSize = message.audio.file_size;
        } else if (message.video) {
            fName = message.video.file_name || "Video File";
            fType = message.video.mime_type ? message.video.mime_type.split("/")[0] : "video";
            fSize = message.video.file_size;
        } else if (message.photo) {
            const uniqueId = message.photo[message.photo.length - 1].file_unique_id;
            fName = `${uniqueId}.jpg`;
            fType = "image";
            fSize = message.photo[message.photo.length - 1].file_size;
        }

        // --- 5b. Size Check ---
        if (fSize > MAX_TELEGRAM_SIZE) {
            return Bot.sendMessage(message.chat.id, message.message_id, 
                `❌ *ғɪʟᴇ ᴛᴏᴏ ʟᴀʀɢᴇ*\n\n` +
                `📊 *ғɪʟᴇ sɪᴢᴇ:* \`${formatSize(fSize)}\`\n` +
                `⚠️ *ᴍᴀx ᴀʟʟᴏᴡᴇᴅ:* \`4.00 GB\`\n\n` +
                `Please send a smaller file.`);
        }

        // --- 5c. Copy the Message to Channel ---
        fSave = await Bot.copyMessage(BOT_CHANNEL, message.chat.id, message.message_id);

    } else {
        const buttons = [[{ text: "Source Code", url: "https://github.com/vauth/filestream-cf" }]];
        return Bot.sendMessage(message.chat.id, message.message_id, "Send me any file/video/gif/audio *(max 4GB)*.", buttons)
    }

    // 6. Check if Forwarding Failed
    if (fSave.error_code) {
        return Bot.sendMessage(message.chat.id, message.message_id, "❌ Error forwarding to channel:\n" + fSave.description);
    }

    // 7. Generate Links & Buttons
    try {
        if (!fSave.message_id) {
            return Bot.sendMessage(message.chat.id, message.message_id, "❌ Error: Channel did not return a message ID.");
        }

        const final_hash = await Cryptic.Hash(fSave.message_id);
        const final_link = `${url.origin}/?file=${final_hash}`;
        const final_tele = `https://t.me/${bot.username}/?start=${final_hash}`;
        const stream_page = `${url.origin}/stream?file=${final_hash}`;
        const formattedSize = formatSize(fSize);
        
        // Determine if file is streamable (Video or Audio)
        const isStreamable = (fType === 'video' || fType === 'audio');

        // --- Define Buttons ---
        const btnStream = { text: "🌐 sᴛʀᴇᴀᴍ ᴘᴀɢᴇ", url: stream_page };
        const btnDownload = { text: "📥 ᴅᴏᴡɴʟᴏᴀᴅ", url: final_link };
        const btnTele = { text: "💬 ᴛᴇʟᴇɢʀᴀᴍ", url: final_tele };
        const btnShare = { text: "🔁 sʜᴀʀᴇ", switch_inline_query: final_hash };
        const btnOwner = { text: "👑 ᴏᴡɴᴇʀ", url: `https://t.me/${OWNER_USERNAME}` };

        let buttons = [];

        if (isStreamable) {
            buttons = [
                [btnStream, btnDownload],
                [btnTele, btnShare],
                [btnOwner]
            ];
        } else {
            // If it's a document/zip/exe, don't show Stream or VLC buttons
            buttons = [
                [btnDownload, btnTele],
                [btnShare],
                [btnOwner]
            ];
        }

        // --- Define Message Text ---
        // Escape the filename to prevent markdown errors!
        const safeName = escapeMarkdown(fName);
        
        let final_text = `✅ *ғɪʟᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴘʀᴏᴄᴇssᴇᴅ!*\n\n` +
            `📂 *ғɪʟᴇ ɴᴀᴍᴇ:* \`${safeName}\`\n` +
            `💾 *ғɪʟᴇ sɪᴢᴇ:* \`${formattedSize}\`\n` +
            `📊 *ғɪʟᴇ ᴛʏᴘᴇ:* \`${fType}\`\n`;

        if (isStreamable) {
            final_text += `🎬 *sᴛʀᴇᴀᴍɪɴɢ:* \`Available\`\n\n`;
            final_text += `🔗 *sᴛʀᴇᴀᴍ ʟɪɴᴋ:*\n\`${stream_page}\``;
            
            if (fSize > MAX_STREAM_SIZE) {
                final_text += `\n\n⚠️ *ɴᴏᴛᴇ:* Streaming works best for files under 2GB.`;
            }
        } else {
            final_text += `\n🔗 *ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ:*\n\`${final_link}\``;
        }

        return Bot.sendMessage(message.chat.id, message.message_id, final_text, buttons);

    } catch (error) {
        return Bot.sendMessage(message.chat.id, message.message_id, "❌ **Critical Error:**\n" + error.message);
    }
}