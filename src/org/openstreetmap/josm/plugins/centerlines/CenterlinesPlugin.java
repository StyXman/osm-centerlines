package org.openstreetmap.josm.plugins.centerlines;

import org.openstreetmap.josm.plugins.Plugin;
import org.openstreetmap.josm.data.projection.Projection;
import org.openstreetmap.josm.actions.JosmAction;

import org.openstreetmap.josm.plugins.PluginInformation;
import org.openstreetmap.josm.plugins.centerlines.CenterlinesAction;
import org.openstreetmap.josm.gui.MainMenu;
import org.openstreetmap.josm.Main;
import org.openstreetmap.josm.gui.preferences.projection.ProjectionPreference;
// import org.openstreetmap.josm.plugins.centerlines.SelectionManager;

import org.openstreetmap.josm.data.osm.DataSet;
import java.util.Collection;
import org.openstreetmap.josm.data.osm.OsmPrimitive;
import org.openstreetmap.josm.data.osm.Way;
import java.util.ArrayList;

import java.io.InputStream;
import java.io.IOException;
import java.lang.ProcessBuilder;
import java.lang.Process;

import java.io.StringWriter;
import javax.json.Json;
import javax.json.JsonWriter;
import javax.json.JsonArrayBuilder;
import javax.json.JsonObjectBuilder;

import org.openstreetmap.josm.data.osm.Node;
import org.openstreetmap.josm.data.coor.LatLon;

import org.openstreetmap.josm.data.coor.EastNorth;
import java.math.BigDecimal;
import java.math.RoundingMode;

import javax.json.JsonObject;
import javax.json.JsonArray;
import javax.json.JsonReader;
import java.io.StringReader;
import javax.json.JsonValue;
import org.openstreetmap.josm.data.coor.LatLon;
import javax.json.JsonNumber;


// a lot of code taken from other plugins and core code, like:
// MichiganLeft
// GeoJSONWriter

public class CenterlinesPlugin extends Plugin {
    private static JosmAction menuEntry;
    private final Projection projection;

    /**
     * Will be invoked by JOSM to bootstrap the plugin
     *
     * @param info  information about the plugin and its local installation
     */
    public CenterlinesPlugin(PluginInformation info) {
        super(info);

        // menu entry
        this.menuEntry = new CenterlinesAction(this);
        MainMenu.add(Main.main.menu.moreToolsMenu, menuEntry);

        this.projection = ProjectionPreference.wgs84.getProjection();
    }


    public void execute() {
        DataSet dataSet = Main.getLayerManager().getEditDataSet();
        Collection<OsmPrimitive> mainSelection = dataSet.getSelected();

        ArrayList<Way> valid_ways = new ArrayList<>();

        for (OsmPrimitive prim : mainSelection) {
            if (prim instanceof Way) {
                Way way = (Way) prim; // casting :)

                if (way.isClosed()) {
                    valid_ways.add(way);
                }
            }
        }

        System.out.println(this.wayToJSON(valid_ways));
        String json = call_script(this.wayToJSON(valid_ways));
        System.out.println(json);
        ArrayList<Way> centerlines = this.JSONtoWays(json);
        System.out.println(this.wayToJSON(centerlines));

        for (Way centerline : centerlines) {
            for (Node node : centerline.getNodes()) {
                // TODO: check existence
                dataSet.addPrimitive(node);
            }
            dataSet.addPrimitive(centerline);
        }
    }


    private String call_script(String input_json) {
        ProcessBuilder builder = new ProcessBuilder("centerlines.py");
        String ans = "";

        try {
            Process script = builder.start ();
            InputStream output = script.getInputStream();
            byte buffer[] = new byte[1024];

            int i = 0;
            while ( (i = output.read(buffer)) > 0 ) {
                ans+= new String(buffer, 0, i);
            }
        } catch (IOException e) {
            // I can't give a partial answer, so this for the moment
            // TODO: real error handling
            return "";
        }

        return ans;
    }

    private String wayToJSON(ArrayList<Way> ways) {
        // this API is *so* *fucking* *useless*
        StringWriter json = new StringWriter();
        JsonWriter writer = Json.createWriter(json);

        JsonArrayBuilder features = Json.createArrayBuilder();

        for (Way w : ways) {
            JsonArrayBuilder coords = Json.createArrayBuilder();
            coords.add(this.getCoordsArray(w.getNodes()));

            // why a Model decision is made based on a View algorithm?
            // fuck ElemStyles, I'm doing it my way (pun not intended)
            JsonObjectBuilder way = Json.createObjectBuilder();
            way.add("type", "Polygon");
            way.add("coordinates", coords);

            JsonObjectBuilder feature = Json.createObjectBuilder();
            feature.add("type", "Feature");
            // I don't give a flying fuck about properties
            feature.add("geometry", way);

            features.add(feature);
        }

        JsonObjectBuilder collection = Json.createObjectBuilder();
        collection.add("type", "FeatureCollection");
        collection.add("features", features);

        // this is why the class is JsonObject*Builder*
        writer.writeObject(collection.build());

        return json.toString();
    }

    private JsonArrayBuilder getCoordsArray(Iterable<Node> nodes) {
        final JsonArrayBuilder builder = Json.createArrayBuilder();
        for (Node n : nodes) {
            LatLon ll = n.getCoor();
            if (ll != null) {
                builder.add(getCoordArray(null, ll));
            }
        }
        return builder;
    }

    private JsonArrayBuilder getCoordArray(JsonArrayBuilder builder, LatLon c) {
        return getCoordArray(builder, this.projection.latlon2eastNorth(c));
    }

    private static JsonArrayBuilder getCoordArray(JsonArrayBuilder builder, EastNorth c) {
        return builder != null ? builder : Json.createArrayBuilder()
                .add(BigDecimal.valueOf(c.getX()).setScale(11, RoundingMode.HALF_UP))
                .add(BigDecimal.valueOf(c.getY()).setScale(11, RoundingMode.HALF_UP));
    }


    private ArrayList<Way> JSONtoWays (String json) {
        JsonReader reader = Json.createReader(new StringReader(json));
        JsonObject collection = reader.readObject();
        ArrayList<Way> ways = new ArrayList<>();

        JsonArray features = collection.getJsonArray("features");

        for (JsonValue value : features) {
            // yougottabefuckingkiddingme
            JsonObject feature = (JsonObject) value;
            JsonObject geometry = feature.getJsonObject("geometry");

            // bloody compiler, you could say something about using ==, right?
            if (geometry.getString("type").equals("MultiLineString")) {
                JsonArray lineStrings = geometry.getJsonArray("coordinates");

                if (lineStrings == null) {
                    StringWriter foo = new StringWriter();
                    JsonWriter writer = Json.createWriter(foo);

                    writer.writeObject (geometry);

                    System.err.println("geometry without coords?: "+foo.toString());

                    continue;
                }

                // NPE!
                for (JsonValue value1: lineStrings) {
                    JsonArray lineString = (JsonArray) value1;
                    Way way = new Way();

                    for (JsonValue value2 : lineString) {
                        JsonArray point = (JsonArray) value2;
                        JsonNumber x = point.getJsonNumber(0);
                        JsonNumber y = point.getJsonNumber(1);
                        // ERROR: java.lang.ClassCastException: org.glassfish.json.JsonNumberImpl$JsonBigDecimalNumber cannot be cast to javax.json.JsonString
                        EastNorth en = new EastNorth(x.doubleValue(), y.doubleValue());
                        LatLon latlon = this.projection.eastNorth2latlon(en);
                        Node node = new Node(latlon);

                        way.addNode(node);
                    }

                    ways.add(way);
                }
            } else {
                StringWriter foo = new StringWriter();
                JsonWriter writer = Json.createWriter(foo);

                writer.writeObject (geometry);

                System.err.println(">"+geometry.getString("type")+"<");
                System.err.println("Unknown geometry: "+foo.toString());
            }
        }

        return ways;
    }
}
