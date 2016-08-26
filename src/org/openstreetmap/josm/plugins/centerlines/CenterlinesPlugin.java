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

        for (OsmPrimitive prim : mainSelection) {
            if (prim instanceof Way) {
                Way way = (Way) prim; // casting :)

                if (way.isClosed()) {
                    /*
                    // simulate some work by creating a new Way that goes from way[0] to way[2]
                    if (way.getNodes().size()>2) {
                        System.out.println("BAM!");

                        Way new_way = new Way();
                        new_way.addNode(way.getNode(0));
                        new_way.addNode(way.getNode(2));

                        dataSet.addPrimitive(new_way);
                    }
                    */
                    System.out.println(this.wayToJSON(way));
                }
            }
        }
    }

    private String wayToJSON(Way w) {
        /*
{
    "type": "FeatureCollection",
    "features": [ {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
                [100.0, 0.0] ]
             ]
        }
    } ]
}
        */

        // this API is *so* *fucking* *useless*
        StringWriter json = new StringWriter();
        JsonWriter writer = Json.createWriter(json);

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

        JsonArrayBuilder features = Json.createArrayBuilder();
        features.add(feature);

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
        return getCoorArray(builder, projection.latlon2eastNorth(c));
    }

    private static JsonArrayBuilder getCoorArray(JsonArrayBuilder builder, EastNorth c) {
        return builder != null ? builder : Json.createArrayBuilder()
                .add(BigDecimal.valueOf(c.getX()).setScale(11, RoundingMode.HALF_UP))
                .add(BigDecimal.valueOf(c.getY()).setScale(11, RoundingMode.HALF_UP));
    }
}
