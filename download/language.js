(function () {
  'use strict';
  const languages = window.TempoDownloadLanguages;
  const select = document.getElementById('language');
  const params = new URLSearchParams(location.search);
  let saved;
  try { saved = localStorage.getItem('tempo-download-language'); } catch (_) {}
  function apply(code) {
    const key = Object.hasOwn(languages, code) ? code : 'en';
    const text = languages[key];
    document.documentElement.lang = text.lang;
    document.documentElement.dir = text.dir;
    document.title = text.download + ' TEMPO · DailyDrum';
    document.querySelector('.eyebrow').textContent = text.eyebrow;
    document.getElementById('download-heading').textContent = text.download;
    document.querySelector('.intro').textContent = text.intro;
    document.querySelector('.stores').setAttribute('aria-label', text.download);
    document.getElementById('status').textContent = text.cta;
    const privacy = document.querySelector('footer a');
    privacy.textContent = text.privacy;
    // Preserve the existing privacy-policy destination.
    privacy.href = 'https://tempo.dailydrum.co.kr/privacy.html';
    document.querySelector('.brand').href = 'https://tempo.dailydrum.co.kr/' + (key === 'ko' ? '' : key + '/');
    select.value = key;
  }
  apply(params.get('lang') || saved || 'en');
  select.addEventListener('change', function () {
    apply(select.value);
    try { localStorage.setItem('tempo-download-language', select.value); } catch (_) {}
    const url = new URL(location.href);
    url.searchParams.set('lang', select.value);
    history.replaceState(null, '', url);
  });
})();
