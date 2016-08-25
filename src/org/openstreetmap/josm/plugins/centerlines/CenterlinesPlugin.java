package org.openstreetmap.josm.plugins.centerlines;

import org.openstreetmap.josm.plugins.Plugin;
import org.openstreetmap.josm.plugins.PluginInformation;

import org.openstreetmap.josm.actions.JosmAction;
import org.openstreetmap.josm.gui.MainMenu;
import org.openstreetmap.josm.Main;

import org.openstreetmap.josm.plugins.centerlines.CenterlinesAction;

public class CenterlinesPlugin extends Plugin {
    private static JosmAction menuEntry;
    /**
     * Will be invoked by JOSM to bootstrap the plugin
     *
     * @param info  information about the plugin and its local installation
     */
    public CenterlinesPlugin(PluginInformation info) {
        super(info);
        // init your plugin

        this.menuEntry = new CenterlinesAction();
        MainMenu.add(Main.main.menu.moreToolsMenu, menuEntry);
    }
}
