
/*
  Created by Jon Wyatt on 13/10/15 (copied from Colin Wren 29/06/15).
 */

describe('Axes', function() {

  var context, focus, graph, graphlib, test_area;
  graphlib = null;
  graph = null;
  context = null;
  focus = null;
  test_area = null;

  beforeEach(function() {

    var body_el = document.getElementsByTagName('body')[0];
    test_area = document.createElement('div');
    test_area.setAttribute('id', 'test_area');
    test_area.style.width = '500px';
    body_el.appendChild(test_area);

    if (graphlib === null) {
      graphlib = new NHGraphLib('#test_area');
    }
    if (graph === null) {
      graph = new NHGraph();
    }
    if (context === null) {
      context = new NHContext();
    }
    if (focus === null) {
      focus = new NHFocus();
    }

    graph.options.keys = ['respiration_rate'];
    graph.options.label = 'RR';
    graph.options.measurement = '/min';
    graph.axes.y.min = 0;
    graph.axes.y.max = 60;
    graph.options.normal.min = 12;
    graph.options.normal.max = 20;
    graph.style.dimensions.height = 250;
    graph.style.data_style = 'linear';
    graph.style.label_width = 60;

    focus.graphs.push(graph);
    graphlib.focus = focus;

    graphlib.data.raw = ews_data.single_record;

  });


  afterEach(function() {

    if (graphlib !== null) {
      graphlib = null;
    }

    if (graph !== null) {
      graph = null;
    }

    if (context !== null) {
      context = null;
    }

    if (focus !== null) {
      focus = null;
    }

    if (test_area !== null) {
      test_area.parentNode.removeChild(test_area);
    }

    var pops = document.querySelectorAll('#chart_popup');
    if (pops.length > 0) {
      for (j = 0, len = pops.length; j < len; j++) {
        pop = pops[j];
        pop.parentNode.removeChild(pop);
      }
    }
    var tests = document.querySelectorAll('#test_area');
    if (tests.length > 0) {
      for (k = 0, len1 = tests.length; k < len1; k++) {
        test = tests[k];
        test.parentNode.removeChild(test);
      }
    }
  });


  describe("NHGraphLib, NHContext, NHFocus, NHGraph axes properties", function() {

    it('NHGraphLib has properties for setting the axis label height', function() {
      expect(graphlib.style.hasOwnProperty('axis_label_text_height')).toBe(true);
    });

    it('NHContext has axes property that holds information for X and Y axes', function() {
      expect(context.hasOwnProperty('axes')).toBe(true);
      expect(context.axes.hasOwnProperty('x')).toBe(true);
      expect(context.axes.hasOwnProperty('y')).toBe(true);
      expect(context.axes.x.hasOwnProperty('scale')).toBe(true);
      expect(context.axes.x.hasOwnProperty('axis')).toBe(true);
      expect(context.axes.x.hasOwnProperty('min')).toBe(true);
      expect(context.axes.x.hasOwnProperty('max')).toBe(true);
      expect(context.axes.y.hasOwnProperty('scale')).toBe(true);
      expect(context.axes.y.hasOwnProperty('axis')).toBe(true);
      expect(context.axes.y.hasOwnProperty('min')).toBe(true);
      expect(context.axes.y.hasOwnProperty('max')).toBe(true);
    });

    it('NHFocus has axes property that holds information for X and Y axes', function() {
      expect(focus.hasOwnProperty('axes')).toBe(true);
      expect(focus.axes.hasOwnProperty('x')).toBe(true);
      expect(focus.axes.hasOwnProperty('y')).toBe(true);
      expect(focus.axes.x.hasOwnProperty('scale')).toBe(true);
      expect(focus.axes.x.hasOwnProperty('axis')).toBe(true);
      expect(focus.axes.x.hasOwnProperty('min')).toBe(true);
      expect(focus.axes.x.hasOwnProperty('max')).toBe(true);
      expect(focus.axes.y.hasOwnProperty('scale')).toBe(true);
      expect(focus.axes.y.hasOwnProperty('axis')).toBe(true);
      expect(focus.axes.y.hasOwnProperty('min')).toBe(true);
      expect(focus.axes.y.hasOwnProperty('max')).toBe(true);
    });

    it('NHGraph has axes property that holds information for X and Y axes', function() {
      expect(graph.hasOwnProperty('axes')).toBe(true);
      expect(graph.axes.hasOwnProperty('x')).toBe(true);
      expect(graph.axes.hasOwnProperty('y')).toBe(true);
      expect(graph.axes.hasOwnProperty('obj')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('scale')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('axis')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('min')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('max')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('obj')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('scale')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('axis')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('min')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('max')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('obj')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('ranged_extent')).toBe(true);
    });

    it('NHGraph has styling properties for X and Y axes', function() {
      expect(graph.style.hasOwnProperty('axis')).toBe(true);
      expect(graph.style.hasOwnProperty('axis_label_text_height')).toBe(true);
      expect(graph.style.hasOwnProperty('axis_label_text_padding')).toBe(true);
      expect(graph.style.axis.hasOwnProperty('x')).toBe(true);
      expect(graph.style.axis.hasOwnProperty('y')).toBe(true);
      expect(graph.style.axis.x.hasOwnProperty('hide')).toBe(true);
      expect(graph.style.axis.y.hasOwnProperty('hide')).toBe(true);
      expect(graph.style.axis.x.hasOwnProperty('size')).toBe(true);
      expect(graph.style.axis.y.hasOwnProperty('size')).toBe(true);
    });
  });

  describe("Structure", function() {

    beforeEach(function() {
      graphlib.init();
      graphlib.draw();
    });

    it("Creates a DOM structure for the axis which is easy to understand", function() {
      var focus_el, focus_els, graph_el, graph_els, x_el, x_els, y_el, y_els;

      focus_els = document.getElementsByClassName('nhfocus');
      expect(focus_els.length).toBe(1);

      graph_els = document.querySelectorAll('.nhfocus .nhgraph');
      expect(graph_els.length).toBe(1);

      x_els = document.querySelectorAll('.nhgraph .x');
      expect(x_els.length).toBe(1);

      x_el = x_els[0];
      expect(x_el.getAttribute('class')).toBe('x axis');

      y_els = document.querySelectorAll('.nhgraph .y');
      expect(y_els.length).toBe(1);

      y_el = y_els[0];
      expect(y_el.getAttribute('class')).toBe('y axis');
    });
  });

  describe('X-Axis', function() {

    describe("Visibility", function() {

      it("is visible by default", function() {
        graphlib.init();
        expect(document.querySelectorAll('.x').length).toBe(1);
      });

      it("can be hidden", function() {
        graph.style.axis.x.hide = true;
        graphlib.init();
        expect(document.querySelectorAll('.x').length).toBe(0);
      });
    });

    describe('Scale', function() {
      it('Adds time padding of 6000000 to the scale when plotting a single data point and no time padding defined', function() {
        var data_point, end, ends, start, starts, terminated;
        terminated = graphlib.data.raw[0]['date_terminated'];
        data_point = graphlib.date_from_string(terminated);
        graphlib.init();
        expect(graphlib.style.timePadding).toBe(6000000);
        start = new Date(data_point);
        end = new Date(data_point);
        start.setMinutes(start.getMinutes() - 100);
        end.setMinutes(end.getMinutes() + 100);
        starts = graphlib.date_to_string(start);
        ends = graphlib.date_to_string(end);
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(starts);
        expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(ends);
      });

      it('Adds time padding of 3 minutes to the scale when plotting a single data point and time padding of 180,000 is defined', function() {
        var data_point, end, ends, start, starts, terminated;
        terminated = graphlib.data.raw[0]['date_terminated'];
        data_point = graphlib.date_from_string(terminated);
        graphlib.style.timePadding = 180000;
        graphlib.init();
        expect(graphlib.style.timePadding).toBe(180000);
        start = new Date(data_point);
        end = new Date(data_point);
        start.setMinutes(start.getMinutes() - 3);
        end.setMinutes(end.getMinutes() + 3);
        starts = graphlib.date_to_string(start);
        ends = graphlib.date_to_string(end);
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(starts);
        expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(ends);
      });

      it('Adds time padding of 5% of the total time range when plotting multiple data points and no time padding defined', function() {
        var end, ends, original_extent, raw1, raw2, start, starts, term1, term2;
        graphlib.data.raw = ews_data.multiple_records;
        raw1 = graphlib.data.raw[0]['date_terminated'];
        raw2 = graphlib.data.raw[1]['date_terminated'];
        term1 = graphlib.date_from_string(raw1);
        term2 = graphlib.date_from_string(raw2);
        original_extent = [term1, term2]; // One hour difference.
        graphlib.init();
        var fivePercentOfOneHourInMinutes = 3
        var fivePercentOfOneHourInMilliseconds = 180000
        expect(graphlib.style.timePadding).toBe(fivePercentOfOneHourInMilliseconds);
        start = new Date(original_extent[0]);
        end = new Date(original_extent[1]);
        start.setMinutes(start.getMinutes() - fivePercentOfOneHourInMinutes);
        end.setMinutes(end.getMinutes() + fivePercentOfOneHourInMinutes);
        starts = graphlib.date_to_string(start);
        ends = graphlib.date_to_string(end);
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(starts);
        expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(ends);
      });

      it('Adds time padding of 3 minutes to the scale when plotting multiple data points when time padding of 180000 is defined', function() {
        var end, ends, original_extent, raw1, raw2, start, starts, term1, term2;
        graphlib.data.raw = ews_data.multiple_records;
        raw1 = graphlib.data.raw[0]['date_terminated'];
        raw2 = graphlib.data.raw[1]['date_terminated'];
        term1 = graphlib.date_from_string(raw1);
        term2 = graphlib.date_from_string(raw2);
        original_extent = [term1, term2];
        graphlib.style.timePadding = 180000;
        graphlib.init();
        expect(graphlib.style.timePadding).toBe(180000);
        start = new Date(original_extent[0]);
        end = new Date(original_extent[1]);
        start.setMinutes(start.getMinutes() - 3);
        end.setMinutes(end.getMinutes() + 3);
        starts = graphlib.date_to_string(start);
        ends = graphlib.date_to_string(end);
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(starts);
        expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(ends);
      });
    });

    describe('Ticks', function() {

      it("has sensible amount", function() {
        var x_ticks;
        graphlib.init();
        graphlib.draw();

        x_ticks = document.querySelectorAll('.x .tick');
        expect(x_ticks.length).toBeLessThan(10);
        expect(x_ticks.length).toBeGreaterThan(2);
      });

      it("are evenly spaced", function() {

        var lastGap, tick, xPos, x_ticks;
        graphlib.init();
        graphlib.draw();

        x_ticks = document.querySelectorAll('.x .tick');

        xPos = [];

        for (var j = 0; j < x_ticks.length; j++) {
          tick = x_ticks[j];
          var tickTransformAttribute = tick.getAttribute('transform');
          var tickRegex = /translate\((\d+),\d+\)/;
          var matches = tickRegex.exec(tickTransformAttribute);
          if (matches) {
            var xPosTick = matches[1];
            xPos.push(parseInt(xPosTick));
          }
        }

        lastGap = null;
        for (var i = 1; i < xPos.length; i++) {
          if (lastGap !== null) {
            expect(Math.round(xPos[i] - xPos[i - 1])).toBe(lastGap);
          }
          lastGap = Math.round(xPos[i] - xPos[i - 1]);
        }
      });

      describe('Labels', function() {

        it("use default size if no size defined", function() {
          var j, len, tick, tspans, x_ticks;
          graphlib.init();
          graphlib.draw();
          x_ticks = document.querySelectorAll('.x .tick');
          for (j = 0, len = x_ticks.length; j < len; j++) {
            tick = x_ticks[j];
            tspans = tick.getElementsByTagName('tspan');
            expect(tspans.length).toBe(3);
            expect(tspans[0].getAttribute('x')).toBe(null);
            expect(tspans[0].getAttribute('dy')).toBe(null);
            expect(tspans[0].getAttribute('style')).toBe('font-size: 12px;');
            expect(tspans[1].getAttribute('x')).toBe('0');
            expect(tspans[1].getAttribute('dy')).toBe('14');
            expect(tspans[1].getAttribute('style')).toBe('font-size: 12px;');
            expect(tspans[2].getAttribute('x')).toBe('0');
            expect(tspans[2].getAttribute('dy')).toBe('14');
            expect(tspans[2].getAttribute('style')).toBe('font-size: 12px;');
          }
        });

        it("use defined size if provided", function() {
          var j, len, text_el, tick, tspans, x_ticks;
          graph.style.axis_label_font_size = 30;
          graph.style.axis_label_line_height = 2;
          graphlib.init();
          graphlib.draw();
          x_ticks = document.querySelectorAll('.x .tick');
          for (j = 0, len = x_ticks.length; j < len; j++) {
            tick = x_ticks[j];
            text_el = tick.getElementsByTagName('text');
            expect(text_el.length).toBe(1);
            expect(text_el[0].getAttribute('y')).toBe('-150');
            tspans = tick.getElementsByTagName('tspan');
            expect(tspans.length).toBe(3);

            expect(tspans[0].getAttribute('x')).toBe(null);
            expect(tspans[0].getAttribute('dy')).toBe(null);
            expect(tspans[0].getAttribute('style')).toBe('font-size: 30px;');

            expect(tspans[1].getAttribute('x')).toBe('0');
            expect(tspans[1].getAttribute('dy')).toBe('60');
            expect(tspans[1].getAttribute('style')).toBe('font-size: 30px;');

            expect(tspans[2].getAttribute('x')).toBe('0');
            expect(tspans[2].getAttribute('dy')).toBe('60');
            expect(tspans[2].getAttribute('style')).toBe('font-size: 30px;');
          }
        });

        it("have sensible text values for day / date/ time", function() {
          var date_re, day_re, j, len, tick, time_re, tspans, x_ticks;
          graphlib.init();
          graphlib.draw();
          x_ticks = document.querySelectorAll('.x .tick');
          day_re = new RegExp('[MTWFS][a-z][a-z]');
          date_re = new RegExp('[0-9]?[0-9]/[0-9]?[0-9]/[0-9]?[0-9]');
          time_re = new RegExp('[0-2]?[0-9]:[0-5]?[0-9]');
          for (j = 0, len = x_ticks.length; j < len; j++) {
            tick = x_ticks[j];
            tspans = tick.getElementsByTagName('tspan');
            expect(tspans.length).toBe(3);
            expect(day_re.exec(tspans[0].textContent)).not.toBe(null);
            expect(date_re.exec(tspans[1].textContent)).not.toBe(null);
            expect(time_re.exec(tspans[2].textContent)).not.toBe(null);
          }
        });
      });
    });
  });

  describe('Y-Axis', function() {

    describe("Visibility", function() {

      it("is visible by default", function() {
        graphlib.init();
        expect(document.querySelectorAll('.y').length).toBe(1);
      });

      it("can be hidden", function() {
        graph.style.axis.y.hide = true;
        graphlib.init();
        expect(document.querySelectorAll('.y').length).toBe(0);
      });
    });

    describe('Scale', function() {

      it("Uses min/max values set in graph.axes.y object", function() {
        var lastTick, y_ticks_text;
        graphlib.init();
        graphlib.draw();
        y_ticks_text = document.querySelectorAll('.y .tick text');
        expect(y_ticks_text.length).toBeGreaterThan(3);
        expect(+y_ticks_text[0].textContent).toBe(graph.axes.y.min);
        lastTick = y_ticks_text[y_ticks_text.length - 1].textContent;
        expect(+lastTick).toBe(graph.axes.y.max);
      });
    });

    describe('Steps', function() {

      it("uses strings for values if provided", function(){
         var j, len, tick, y_ticks;
        graph.axes.y.valueLabels = {
            1: 'One',
            2: 'Two'
        };
        graph.axes.y.min = 1;
        graph.axes.y.max = 2;
        graph.style.axis.step = 0;
        graphlib.init();
        graphlib.draw();
        y_ticks = document.querySelectorAll('.y .tick text');
        expect(y_ticks[0].textContent).toBe('One');
        expect(y_ticks[y_ticks.length - 1].textContent).toBe('Two');
      });

      it("changes tick label format as defined", function() {
        var j, len, tick, y_ticks;
        graph.style.axis.step = 2;
        graphlib.init();
        graphlib.draw();
        y_ticks = document.querySelectorAll('.y .tick text');
        for (j = 0, len = y_ticks.length; j < len; j++) {
          tick = y_ticks[j];
          expect(tick.textContent.substr(-2)).toBe('00');
        }
      });
    });
  });
});
