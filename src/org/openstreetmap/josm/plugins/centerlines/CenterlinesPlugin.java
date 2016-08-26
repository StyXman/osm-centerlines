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
        Collection<OsmPrimitive> mainSelection = Main.getLayerManager().getEditDataSet().getSelected();

        for (OsmPrimitive prim : mainSelection) {
            if (this.isClosedWay (prim)) {
                System.out.println("BAM!");
            }
        }
    }

    private boolean isClosedWay(OsmPrimitive prim) {
        if (prim instanceof Way) {
            Way way = (Way) prim; // casting :)

            int last = way.getNodes().size() - 1;
            return ( way.getNode(0) == way.getNode(last) );
        }

        return false;
    }
}
