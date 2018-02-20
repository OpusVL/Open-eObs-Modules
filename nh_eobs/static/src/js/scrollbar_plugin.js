(function($) {
    $.fn.hasVerticalScrollBar = function() {
        return this.get(0) ? this.get(0).scrollHeight > this.height() : false;
    }
})(jQuery);