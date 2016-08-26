package org.openstreetmap.josm.plugins.centerlines;

import org.openstreetmap.josm.plugins.Plugin;
import org.openstreetmap.josm.plugins.PluginInformation;

import org.openstreetmap.josm.actions.JosmAction;
import org.openstreetmap.josm.gui.MainMenu;
import org.openstreetmap.josm.Main;

import org.openstreetmap.josm.plugins.centerlines.CenterlinesAction;
import org.openstreetmap.josm.plugins.centerlines.SelectionManager;

import java.util.Collection;
import org.openstreetmap.josm.data.osm.OsmPrimitive;

import org.openstreetmap.josm.data.osm.DataSet;
import org.openstreetmap.josm.data.osm.Way;


public class CenterlinesPlugin extends Plugin {
    private static JosmAction menuEntry;
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
    }

    public void execute() {
        // a lot of code taken from other plugins, like:
        // MichiganLeft
        DataSet dataSet = Main.getLayerManager().getEditDataSet();
        Collection<OsmPrimitive> mainSelection = dataSet.getSelected();

        for (OsmPrimitive prim : mainSelection) {
            if (prim instanceof Way) {
                Way way = (Way) prim; // casting :)

                if (way.isClosed()) {
                    // simulate some work by creating a new Way that goes from way[0] to way[2]
                    if (way.getNodes().size()>2) {
                        System.out.println("BAM!");

                        Way new_way = new Way();
                        new_way.addNode(way.getNode(0));
                        new_way.addNode(way.getNode(2));

                        dataSet.addPrimitive(new_way);
                    }
                }
            }
        }
    }
}
