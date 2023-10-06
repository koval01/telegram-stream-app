(function ($) {
    $.fn.redraw = function () {
        return this.map(function () {
            this.offsetTop;
            return this;
        });
    };
    $.fn.scrollIntoView = function (options) {
        options = options || {}
        return this.first().each(function () {
            let position = options.position || 'auto',
                padding = options.padding || 0,
                duration = options.duration || 0;
            let $item = $(this),
                $cont = $item.scrollParent(),
                scrollTop = $cont.scrollTop(),
                paddingTop = 0,
                itemHeight = $item.outerHeight(),
                isBody = false;
            if ($cont.get(0) === document) {
                isBody = true;
                $cont = $(window);
                positionTop = $item.offset().top;
                paddingTop = $('header').height() + 1;
            } else {
                positionTop = $item.offset().top - $cont.offset().top + scrollTop;
            }
            if (options.slidedEl) {
                if (options.slidedEl === 'this') {
                    options.slidedEl = this;
                }
                $(options.slidedEl, this).each(function () {
                    itemHeight += (this.scrollHeight - this.clientHeight);
                });
            }
            let itemTop = positionTop,
                itemBottom = itemTop + itemHeight,
                contHeight = $cont.height(),
                contTop = scrollTop + padding + paddingTop,
                contBottom = scrollTop + contHeight - padding,
                scrollTo = null;
            if (position === 'auto') {
                if (itemTop < contTop) {
                    scrollTo = itemTop - padding - paddingTop;
                } else if (itemBottom > contBottom) {
                    if (itemHeight > contHeight - padding - padding) {
                        scrollTo = itemTop - padding - paddingTop;
                    } else {
                        scrollTo = itemBottom - contHeight + padding;
                    }
                }
            } else if (position === 'top' || position === 'center') {
                if (contHeight > itemHeight) {
                    padding = (contHeight - paddingTop - itemHeight) / 2;
                }
                scrollTo = itemTop - padding - paddingTop;
            } else if (position === 'bottom') {
                if (itemHeight > contHeight - padding - padding) {
                    scrollTo = itemTop - padding - paddingTop;
                } else {
                    scrollTo = itemBottom - contHeight + padding;
                }
            }
            if (scrollTo) {
                if (duration) {
                    if (isBody) {
                        $cont = $('html');
                    }
                    $cont.stop().animate({
                        scrollTop: scrollTo
                    }, duration);
                } else {
                    $cont.scrollTop(scrollTo);
                }
            }
        });
    };
})(jQuery);

function doesSupportThinBoxShadow() {
    if (!window.getComputedStyle) return;
    let div = document.createElement('div');
    div.style.boxShadow = '0 0 0 0.5px black';
    div.style.display = 'none';
    document.body.appendChild(div);
    let box_shadow = window.getComputedStyle(div).boxShadow;
    document.body.removeChild(div);
    return box_shadow.indexOf('0.5') >= 0;
}

function formatDate(datetime) {
    let date = new Date(datetime);
    let cur_date = new Date();
    let j = date.getDate();
    let M = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][date.getMonth()];
    let Y = date.getFullYear();

    if (cur_date.getFullYear() === date.getFullYear()) {
        return M + ' ' + j;
    }
    return M + ' ' + j + ', ' + Y;
}

function getCssProperty(el, prop) {
    if (window.getComputedStyle) {
        return window.getComputedStyle(el, '').getPropertyValue(prop) || null;
    } else if (el.currentStyle) {
        return el.currentStyle[prop] || null;
    }
    return null;
}

function isVisible(el, padding) {
    let node = el;
    let visibility = getCssProperty(node, 'visibility');
    if (visibility === 'hidden') return false;
    while (node) {
        if (node === document.documentElement) break;
        let display = getCssProperty(node, 'display');
        if (display === 'none') return false;
        let opacity = getCssProperty(node, 'opacity');
        if (opacity !== null && opacity < 0.1) return false;
        node = node.parentNode;
    }
    if (el.getBoundingClientRect) {
        padding = +padding || 0;
        let rect = el.getBoundingClientRect();
        let html = document.documentElement;
        if (rect.bottom < padding ||
            rect.right < padding ||
            rect.top > (window.innerHeight || html.clientHeight) - padding ||
            rect.left > (window.innerWidth || html.clientWidth) - padding) {
            return false;
        }
    }
    return true;
}

let TWeb = {
    init: function (options) {
        options = options || {};
        if (!doesSupportThinBoxShadow()) {
            $('body').addClass('thin_box_shadow');
        }
        $('.js-widget_message').each(function () {
            TPost.init(this);
        });
        TWeb.updateServiceDate($('.js-widget_message_wrap'));
        if (options.scrollToPost) {
            TWeb.highlightPost(options.scrollToPost, true);
        } else {
            $('.js-widget_message_wrap').last().scrollIntoView({
                position: 'top'
            });
        }
        $('body').removeClass('no_transitions');
        $('.js-header_search').on('focus', function () {
            $('header.tgme_header').removeClass('search_collapsed');
            $(this).select();
        });
        $('.js-header_search').on('blur', function () {
            $('header.tgme_header').addClass('search_collapsed');
        });
        TWeb.initScroll();
        TWeb.initViews();
        if (window.matchMedia) {
            let darkMedia = window.matchMedia('(prefers-color-scheme: dark)');
            TWeb.toggleTheme(darkMedia.matches);
            darkMedia.addListener(function (e) {
                TWeb.toggleTheme(e.matches);
            });
        }
    },
    toggleTheme: function (dark) {
        $('html').toggleClass('theme_dark', dark);
    },
    initScroll: function () {
        let $document = $(document);
        $document.on('scroll', function () {
            $before = $('.js-messages_more[data-before]');
            $after = $('.js-messages_more[data-after]');
            let wheight = $(window).height();
            let scrollTop = $(window).scrollTop();
            if ($before.length) {
                let bottom = $before.offset().top + $before.height() - scrollTop;
                if (bottom > -wheight * 3) {
                    TWeb.loadMore($before);
                }
            }
            if ($after.length) {
                let top = $after.offset().top - scrollTop;
                if (top < wheight * 3) {
                    TWeb.loadMore($after);
                }
            }
        });
        $document.on('click', '.js-messages_more', function () {
            let $el = $(this);
            TWeb.loadMore($el);
        });
    },
    initViews: function () {
        TWeb.viewsMap = {};
        TWeb.viewsQueue = [];
        TWeb.viewsLastLoad = 0;
        let $document = $(document),
            $window = $(window);
        $document.ready(function () {
            $window.on('scroll resize', TWeb.checkVisiblePosts);
            TWeb.checkVisiblePosts();
        });
    },
    checkVisiblePosts: function () {
        $('.js-widget_message[data-view]').each(function () {
            if (isVisible(this, 50)) {
                let view = this.getAttribute('data-view');
                if (view) {
                    TWeb.addViewToQueue(view);
                }
                this.removeAttribute('data-view');
            }
        });
    },
    addViewToQueue: function (view) {
        if (!TWeb.viewsMap[view]) {
            TWeb.viewsMap[view] = true;
            TWeb.viewsQueue.push(view);
            TWeb.sendViewsMaybe();
        }
    },
    sendViewsMaybe: function () {
        let now = +(new Date);
        if (now - TWeb.viewsLastLoad < 10000 && TWeb.viewsQueue.length < 50) {
            return setTimeout(TWeb.sendViewsMaybe, 10000);
        }
        if (TWeb.viewsQueue.length > 0) {
            let views = TWeb.viewsQueue.join(';');
            TWeb.viewsQueue = [];
            $.ajax('/v/', {
                type: 'POST',
                data: {
                    views: views
                }
            });
            TWeb.viewsLastLoad = now;
        }
    },
    highlightPost: function (post_id, scroll) {
        let $postWrap = $('.js-widget_message[data-post="' + post_id + '"]').parents('.js-widget_message_wrap');
        if (scroll) {
            $postWrap.scrollIntoView({
                position: 'top'
            });
        }
        $postWrap.addClass('prepare_highlight').redraw().addClass('highlight');
        setTimeout(function () {
            $postWrap.removeClass('highlight');
            setTimeout(function () {
                $postWrap.removeClass('prepare_highlight');
            }, 300);
        }, 1500);
    },
    updateServiceDate: function ($wrapEls, skip_first) {
        $wrapEls.each(function () {
            if (!$(this).data('msg_date')) {
                let datetime = $('time[datetime]', this).attr('datetime');
                if (datetime) {
                    let date_formatted = formatDate(datetime);
                    $('<div class="tgme_widget_message_service_date_wrap"><div class="tgme_widget_message_service_date">' + date_formatted + '</div></div>').appendTo(this);
                    $(this).data('msg_date', date_formatted);
                }
            }
        });
        let len = $wrapEls.size();
        for (let i = len - 1; i >= 0; i--) {
            let $wrapEl = $wrapEls.eq(i);
            let $prevWrapEl = i > 0 ? $wrapEls.eq(i - 1) : null;
            if (!$prevWrapEl && skip_first) continue;
            let date_visible = !$prevWrapEl || $prevWrapEl.data('msg_date') !== $wrapEl.data('msg_date');
            $wrapEl.toggleClass('date_visible', date_visible);
        }
    },
    loadMore: function ($moreEl) {
        let loading = $moreEl.data('loading');
        if (loading) {
            return false;
        }
        let before = $moreEl.attr('data-before');
        let after = $moreEl.attr('data-after');
        let url = $moreEl.attr('href');
        $moreEl.data('loading', true);
        $moreEl.addClass('dots-animated');

        let time0 = +(new Date);
        console.log('loading...', before, after);
        let _load = function (url, before, after) {
            $.ajax(url, {
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                    let time1 = +(new Date);
                    console.log('loaded ' + (time1 - time0) + 'ms');
                    let $data = $(data);
                    let $helper = $('<div class="tgme_widget_messages_helper"></div>');
                    $helper.append($data);
                    $('.js-message_history').append($helper);
                    $helper.find('.js-widget_message').each(function () {
                        TPost.init(this);
                    });
                    $helper.remove();
                    let wrapEls = $data.filter('.js-widget_message_wrap').get();
                    let time2 = +(new Date);
                    console.log('prepared ' + (time2 - time1) + 'ms');
                    let $moreElWrap = $moreEl.parents('.js-messages_more_wrap');
                    if (before) {
                        let firstWrapEl = $moreElWrap.next('.js-widget_message_wrap').get();
                        let $wrapEls = $(wrapEls.concat(firstWrapEl));
                        TWeb.updateServiceDate($wrapEls);
                        let y = $moreElWrap.offset().top + $moreElWrap.outerHeight(true) - $(document).scrollTop();
                        $data.insertBefore($moreElWrap);
                        let st = $moreElWrap.offset().top - y;
                        $moreElWrap.remove();
                        $(window).scrollTop(st);
                    } else {
                        let lastWrapEl = $moreElWrap.prev('.js-widget_message_wrap').get();
                        let $wrapEls = $(lastWrapEl.concat(wrapEls));
                        TWeb.updateServiceDate($wrapEls, lastWrapEl.length > 0);
                        $data.insertBefore($moreElWrap);
                        $moreElWrap.remove();
                    }
                    let time3 = +(new Date);
                    console.log('inserted ' + (time3 - time2) + 'ms');
                },
                error: function (data) {
                    let timeout = $moreEl.data('timeout') || 1000;
                    $moreEl.data('timeout', timeout > 60000 ? timeout : timeout * 2);
                    setTimeout(function () {
                        _load(url, before, after);
                    }, timeout);
                }
            });
        };
        _load(url, before, after);
    }
}
window.TWeb = TWeb;
