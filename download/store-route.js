(function (root) {
  'use strict';
  const stores = Object.freeze({
    ios: 'https://apps.apple.com/app/id6808595998',
    android: 'https://play.google.com/store/apps/details?id=com.dailydrum.metronome'
  });
  function destination({userAgent = '', platform = '', maxTouchPoints = 0, search = ''} = {}) {
    if (new URLSearchParams(search).has('choose')) return null;
    // Embedded/unknown browsers keep both explicit HTTPS buttons. No intents,
    // app schemes, personal identifiers, or user-provided redirect targets.
    if (/KAKAOTALK|NAVER|Instagram|FBAN|FBAV|FB_IAB|Line\/|; wv\)|\bwv\b|GSA\/|TikTok|Bytedance|DaumApps|Snapchat|Twitter/i.test(userAgent)) return null;
    const ios = /iPhone|iPad|iPod/i.test(userAgent) || platform === 'MacIntel' && maxTouchPoints > 1;
    if (ios && /Version\/.*Safari\/|CriOS\/|FxiOS\/|EdgiOS\//.test(userAgent)) return stores.ios;
    if (/Android/i.test(userAgent) && /Chrome\/|Firefox\/|SamsungBrowser\/|EdgA\//.test(userAgent)
        && !/Version\/4\.0/.test(userAgent)) return stores.android;
    return null;
  }
  const api = {stores, destination};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else {
    root.TempoStoreRoute = api;
    const target = destination({userAgent:navigator.userAgent,platform:navigator.platform,maxTouchPoints:navigator.maxTouchPoints,search:location.search});
    if (target) {
      document.getElementById('status').textContent = '스토어로 이동합니다.';
      location.replace(target);
    }
  }
})(typeof window !== 'undefined' ? window : this);
