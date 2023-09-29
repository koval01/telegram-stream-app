// Helper function to check if the browser supports thin box shadow
function doesSupportThinBoxShadow() {
    if (!window.getComputedStyle) return;
    var div = document.createElement('div');
    div.style.boxShadow = '0 0 0 0.5px black';
    div.style.display = 'none';
    document.body.appendChild(div);
    var boxShadow = window.getComputedStyle(div).boxShadow;
    document.body.removeChild(div);
    return boxShadow.indexOf('0.5') >= 0;
}

// Helper function to format a date
function formatDate(datetime) {
    var date = new Date(datetime);
    var curDate = new Date();
    var j = date.getDate();
    var M = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ][date.getMonth()];
    var Y = date.getFullYear();
    if (curDate.getFullYear() == date.getFullYear()) {
        return M + ' ' + j;
    }
    return M + ' ' + j + ', ' + Y;
}

// Helper function to get a CSS property value
function getCssProperty(el, prop) {
    if (window.getComputedStyle) {
        return window.getComputedStyle(el, '').getPropertyValue(prop) || null;
    } else if (el.currentStyle) {
        return el.currentStyle[prop] || null;
    }
    return null;
}

// Helper function to check if an element is visible
function isVisible(el, padding) {
    var node = el;
    var visibility = getCssProperty(node, 'visibility');
    if (visibility == 'hidden') return false;
    while (node) {
        if (node === document.documentElement) break;
        var display = getCssProperty(node, 'display');
        if (display == 'none') return false;
        var opacity = getCssProperty(node, 'opacity');
        if (opacity !== null && opacity < 0.1) return false;
        node = node.parentNode;
    }
    if (el.getBoundingClientRect) {
        padding = +padding || 0;
        var rect = el.getBoundingClientRect();
        var html = document.documentElement;
        if (rect.bottom < padding || rect.right < padding ||
            rect.top > (window.innerHeight || html.clientHeight) - padding ||
            rect.left > (window.innerWidth || html.clientWidth) - padding) {
            return false;
        }
    }
    return true;
}

// Vanilla JavaScript equivalent of the jQuery code
var TWeb = {
    init: function(options) {
        options = options || {};
        if (!doesSupportThinBoxShadow()) {
            document.body.classList.add('thin_box_shadow');
        }
        var widgetMessages = document.querySelectorAll('.js-widget_message');
        widgetMessages.forEach(function(widgetMessage) {
            TPost.init(widgetMessage);
        });
        TWeb.updateServiceDate(document.querySelectorAll('.js-widget_message_wrap'));
        if (options.scrollToPost) {
            TWeb.highlightPost(options.scrollToPost, true);
        } else {
            var widgetMessageWraps = document.querySelectorAll('.js-widget_message_wrap');
            widgetMessageWraps[widgetMessageWraps.length - 1].scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        document.body.classList.remove('no_transitions');
        var headerSearch = document.querySelector('.js-header_search');
        headerSearch.addEventListener('focus', function() {
            document.querySelector('header.tgme_header').classList.remove('search_collapsed');
            this.select();
        });
        headerSearch.addEventListener('blur', function() {
            document.querySelector('header.tgme_header').classList.add('search_collapsed');
        });
        TWeb.initScroll();
        TWeb.initViews();
        if (window.matchMedia) {
            var darkMedia = window.matchMedia('(prefers-color-scheme: dark)');
            TWeb.toggleTheme(darkMedia.matches);
            darkMedia.addListener(function(e) {
                TWeb.toggleTheme(e.matches);
            });
        }
    },
    toggleTheme: function(dark) {
        document.documentElement.classList.toggle('theme_dark', dark);
    },
    initScroll: function() {
        var beforeElements = document.querySelectorAll('.js-messages_more[data-before]');
        var afterElements = document.querySelectorAll('.js-messages_more[data-after]');
        var wheight = window.innerHeight;
        var scrollTop = window.scrollY;

        function loadMore($el) {
            var bottom = $el.offsetTop + $el.offsetHeight - scrollTop;
            if (bottom > -wheight * 3) {
                TWeb.loadMore($el);
            }
        }

        beforeElements.forEach(function($before) {
            loadMore($before);
        });

        afterElements.forEach(function($after) {
            var top = $after.offsetTop - scrollTop;
            if (top < wheight * 3) {
                TWeb.loadMore($after);
            }
        });

        document.addEventListener('scroll', function() {
            beforeElements.forEach(function($before) {
                loadMore($before);
            });

            afterElements.forEach(function($after) {
                var top = $after.offsetTop - scrollTop;
                if (top < wheight * 3) {
                    TWeb.loadMore($after);
                }
            });
        });

        document.addEventListener('click', function(event) {
            if (event.target.classList.contains('js-messages_more')) {
                TWeb.loadMore(event.target);
            }
        });
    },
    initViews: function() {
        TWeb.viewsMap = {};
        TWeb.viewsQueue = [];
        TWeb.viewsLastLoad = 0;

        document.addEventListener('DOMContentLoaded', function() {
            window.addEventListener('scroll', TWeb.checkVisiblePosts);
            window.addEventListener('resize', TWeb.checkVisiblePosts);
            TWeb.checkVisiblePosts();
        });
    },
    checkVisiblePosts: function() {
        var widgetMessages = document.querySelectorAll('.js-widget_message[data-view]');
        widgetMessages.forEach(function(widgetMessage) {
            if (isVisible(widgetMessage, 50)) {
                var view = widgetMessage.getAttribute('data-view');
                if (view) {
                    TWeb.addViewToQueue(view);
                }
                widgetMessage.removeAttribute('data-view');
            }
        });
    },
    addViewToQueue: function(view) {
        if (!TWeb.viewsMap[view]) {
            TWeb.viewsMap[view] = true;
            TWeb.viewsQueue.push(view);
            TWeb.sendViewsMaybe();
        }
    },
    sendViewsMaybe: function() {
        var now = +(new Date);
        if (now - TWeb.viewsLastLoad < 10000 && TWeb.viewsQueue.length < 50) {
            return setTimeout(TWeb.sendViewsMaybe, 10000);
        }
        if (TWeb.viewsQueue.length > 0) {
            var views = TWeb.viewsQueue.join(';');
            TWeb.viewsQueue = [];
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/v/', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.send('views=' + views);
            TWeb.viewsLastLoad = now;
        }
    },
    highlightPost: function(post_id, scroll) {
        var postWrap = document.querySelector('.js-widget_message[data-post="' + post_id + '"]').closest('.js-widget_message_wrap');
        if (scroll) {
            postWrap.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        postWrap.classList.add('prepare_highlight');
        postWrap.offsetWidth; // Trigger a reflow
        postWrap.classList.add('highlight');
        setTimeout(function() {
            postWrap.classList.remove('highlight');
            setTimeout(function() {
                postWrap.classList.remove('prepare_highlight');
            }, 300);
        }, 1500);
    },
    updateServiceDate: function(wrapEls, skip_first) {
        wrapEls.forEach(function(wrapEl, index) {
            if (!wrapEl.dataset.msg_date) {
                var datetime = wrapEl.querySelector('time[datetime]').getAttribute('datetime');
                if (datetime) {
                    var date_formatted = formatDate(datetime);
                    var dateDiv = document.createElement('div');
                    dateDiv.className = 'tgme_widget_message_service_date_wrap';
                    dateDiv.innerHTML = '<div class="tgme_widget_message_service_date">' + date_formatted + '</div>';
                    wrapEl.appendChild(dateDiv);
                    wrapEl.dataset.msg_date = date_formatted;
                }
            }
            if (index > 0 || !skip_first) {
                var date_visible = !wrapEls[index - 1] || wrapEls[index - 1].dataset.msg_date != wrapEl.dataset.msg_date;
                wrapEl.classList.toggle('date_visible', date_visible);
            }
        });
    },
    loadMore: function($moreEl) {
        var loading = $moreEl.dataset.loading;
        if (loading) {
            return false;
        }
        var before = $moreEl.getAttribute('data-before');
        var after = $moreEl.getAttribute('data-after');
        var url = $moreEl.getAttribute('href');
        $moreEl.dataset.loading = true;
        $moreEl.classList.add('dots-animated');
        var time0 = +(new Date);
        console.log('loading...', before, after);

        function _load(url, before, after) {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', url, true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var time1 = +(new Date);
                    console.log('loaded ' + (time1 - time0) + 'ms');
                    var response = JSON.parse(xhr.responseText);
                    var wrapper = document.createElement('div');
                    wrapper.innerHTML = response;
                    var $helper = document.createElement('div');
                    $helper.className = 'tgme_widget_messages_helper';
                    $helper.appendChild(wrapper);
                    var messageHistory = document.querySelector('.js-message_history');
                    messageHistory.appendChild($helper);
                    var $widgetMessages = $helper.querySelectorAll('.js-widget_message');
                    $widgetMessages.forEach(function(widgetMessage) {
                        TPost.init(widgetMessage);
                    });
                    $helper.remove();
                    var wrapEls = Array.from(wrapper.querySelectorAll('.js-widget_message_wrap'));
                    var time2 = +(new Date);
                    console.log('prepared ' + (time2 - time1) + 'ms');
                    var moreElWrap = $moreEl.closest('.js-messages_more_wrap');
                    if (before) {
                        var firstWrapEl = moreElWrap.nextElementSibling;
                        var $wrapEls = [firstWrapEl].concat(wrapEls);
                        TWeb.updateServiceDate($wrapEls);
                        var y = moreElWrap.offsetTop + moreElWrap.offsetHeight - window.scrollY;
                        messageHistory.insertBefore(wrapper, moreElWrap);
                        var st = moreElWrap.offsetTop - y;
                        moreElWrap.remove();
                        window.scrollTo(0, st);
                    } else {
                        var lastWrapEl = moreElWrap.previousElementSibling;
                        var $wrapEls = [lastWrapEl].concat(wrapEls);
                        TWeb.updateServiceDate($wrapEls, !!lastWrapEl);
                        messageHistory.insertBefore(wrapper, moreElWrap);
                        moreElWrap.remove();
                    }
                    var time3 = +(new Date);
                    console.log('inserted ' + (time3 - time2) + 'ms');
                } else if (xhr.readyState === 4) {
                    var timeout = $moreEl.dataset.timeout || 1000;
                    $moreEl.dataset.timeout = timeout > 60000 ? timeout : timeout * 2;
                    setTimeout(function() {
                        _load(url, before, after);
                    }, timeout);
                }
            };
            xhr.send();
        }

        _load(url, before, after);
    }
};

window.TWeb = TWeb;
