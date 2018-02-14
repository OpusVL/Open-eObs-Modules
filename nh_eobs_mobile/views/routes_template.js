var frontend_routes = {}; (function(_root){
    var _nS = function(c,f,b){
        var e=c.split(f||"."),g=b||_root,d,a;
        for(d=0,a=e.length;d<a;d++){
            g=g[e[d]]=g[e[d]]||{};
        }
        return g;
    }
    var _qS = function(items){
        var qs = '';
        for(var i=0;i<items.length;i++) {
            if(items[i]) qs += (qs ? '&' : '') + items[i]};
        return qs ? ('?' + qs) : '';
    }
    var _s = function(p,s){
        return p+((s===true||(s&&s.secure))?'s':'')+'://';
    }
    var _wA = function(r){
        return {ajax:function(c){
            c=c||{};
            c.url=r.url;
            c.type=r.method;
            return jQuery.ajax(c);
        },
            method:r.method,
            type:r.method,
            url:r.url,
            absoluteURL: function(s){
                return _s('http',s)+'{{ base_url }}'+r.url;
            },
            webSocketURL: function(s){
                return _s('ws',s)+'{{ base_url }}'+r.url;
            }
        }
    }
    {% for route in routes %}
        _nS('{{ route.name }}');
        _root.{{ route.name }} = function({% if route.args_list %}{{ route.args_list }}{% endif %}) {
            return _wA({
                method:"{{ route.method }}",
                {% if route.args %}
                url:"{{ base_url }}{{ route.endpoint }}"
                    {% for arg in route.args %}
                        {% if loop.index >= 2 %}
                           + '/'
                        {% endif %}
                        + (function(k,v) {
                            return v
                           })( "{{ arg }}", {{ arg }})
                    {% endfor %}
                {% else %}
                url:"{{ base_url }}{{ route.endpoint }}"
                {% endif %}
            })
        }
    {% endfor %}
})(frontend_routes)