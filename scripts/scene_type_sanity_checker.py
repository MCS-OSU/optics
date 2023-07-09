from opics_common.scene_types.type_constants import abbrev_types

# this script is for exposing if any of the scen_type abbreviations we have devised are not 'found within each other' in case there is 
# some legacy code that can be tripped up.   Functions in log_constants that use the scene types have been ordered such that the only
# found offending abbrev is op (object permanence from pvoe), which is part of iop (interactive object permanence) and opref (agent object preference)
# By checking the if 'op' is in a filename AFTER we check for iop and opref, we can avoid this problem.


# Here's the output of this script as of 011923
# coll matches 1 scene types
# op matches 3 scene types
# stc matches 1 scene types
# sc matches 1 scene types
# grav matches 1 scene types
# igoal matches 1 scene types
# blockb matches 1 scene types
# inconsb matches 1 scene types
# nobarr matches 1 scene types
# irrat matches 1 scene types
# path matches 1 scene types
# time matches 1 scene types
# multa matches 1 scene types
# opref matches 1 scene types
# agentid matches 1 scene types
# cont matches 1 scene types
# lava matches 1 scene types
# holes matches 1 scene types
# movtarg matches 1 scene types
# iop matches 1 scene types
# obst matches 1 scene types
# occl matches 1 scene types
# ramps matches 1 scene types
# solid matches 1 scene types
# spelim matches 1 scene types
# suprel matches 1 scene types
# tool matches 1 scene types
# math matches 1 scene types
# numcomp matches 1 scene types
# imit matches 1 scene types
# setrot matches 1 scene types
# spatref matches 1 scene types
# reor matches 1 scene types
# tlch matches 1 scene types
# tlas matches 1 scene types
# hidtraj matches 1 scene types
# coltraj matches 1 scene types
# sltk matches 1 scene types
# shell matches 1 scene types

if __name__ == '__main__':
    all_types = []
    all_types.extend(abbrev_types['pvoe'])
    all_types.extend(abbrev_types['avoe'])
    all_types.extend(abbrev_types['inter'])
    for scene_type in all_types:
        match_count = 0
        for compared_scene_type in all_types:
            if scene_type in compared_scene_type:
                match_count += 1
        print(f'{scene_type} matches {match_count} scene types')