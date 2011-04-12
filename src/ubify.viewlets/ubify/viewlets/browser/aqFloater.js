/* aqFloater v1.0.1 - Floats an element that attaches itself to a part of the browser window.
   Copyright (C) 2008 Paul Pham <http://aquaron.com/~jquery/aqFloater>

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
(function($){
   $.fn.aqFloater = function(options) {
      var opts = $.extend({
         offsetX: 0, offsetY: 0, attach: '', duration: 50, opacity: '.9'
      }, options);

      var $obj = this;
      $obj.css({ position: 'absolute', opacity: opts.opacity });

      //$(window).scroll(function () {
         var de = document.documentElement;

         var y = (opts.attach.match(/n/) ? 0
            : (opts.attach.match(/s/)
               ? (de.clientHeight - $obj.outerHeight()-10)
               : Math.round((de.clientHeight-$obj.height())/2)));

         var x = (opts.attach.match(/w/) ? 0
            : (opts.attach.match(/e/)
               ? (de.clientWidth - $obj.outerWidth()-10)
               : Math.round((de.clientWidth-$obj.width())/2)));

         $obj.animate({
            top:  (y + $(document).scrollTop() + opts.offsetY) + 'px',
            left: (x + $(document).scrollLeft() + opts.offsetX) + 'px'
         },{queue:false, duration:opts.duration});
      //});

      //$(window).trigger('scroll');
   };
})(jQuery);
