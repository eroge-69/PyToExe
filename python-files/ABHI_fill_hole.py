# PYTHON script
import os
import ansa
from ansa import*
deck = ansa.constants.NASTRAN

def main():
	#will search for part by their name
	part = base.GetPartFromModuleId("A2448851800")
	_3d_holes = base.CollectEntities(deck,None,"HOLE 3D")
	#we will apply condition to know wheather features are recognized or not
	#if feature not recognied below operation will happen else it wont
	if not _3d_holes:
		base.BCSettingsSetValues({"recognize_holes_3d":True})
		fh = base.FeatureHandler(part)
		fh.clear(True)
		fh.recognize(True)
	#will search for 3D holes in card
	_3d_holes = base.CollectEntities(deck,None,"HOLE 3D")
	base.Or(_3d_holes)
	#will dlete the entity
	holes_to_delete = base.CollectEntities(deck,None,"FACE",filter_visible=True)
	base.DeleteEntity(holes_to_delete)
	base.All()
	#again we will recognized feature for 2D
	base.BCSettingsSetValues({"recognize_holes_2d":True})
	fh = base.FeatureHandler(part)
	fh.clear(True)
	fh.recognize(True)
	_2d_holes = base.CollectEntities(deck,None,"HOLE 2D")
	#to know the diameter of the hole 
	req_dia = []
	for dia in _2d_holes:
		_2d_dia = base.GetEntityCardValues(deck,dia,["Diam./Size"])
		req_dia.append(_2d_dia["Diam./Size"])
	#to fill the hole
	for d in req_dia:
		base.FillHoleGeom(d,False,False,False,True,True,pid_id=5)
	#to take filled faces 
	for_cogs = base.CollectEntities(deck,None,"__PROPERTIES__")
	ent = []
	for _req_ent in for_cogs:
		if _req_ent._id==5:
			ent.append(_req_ent)
	base.Or(ent)
	ents = base.CollectEntities(deck,None,"FACE",False,True)
	#to delete either one faces
	req_xyz = []
	for entity in ents:
		req_xyz.append(base.Cog(entity))
	for xyz in req_xyz:
		to_be_delete = base.NearestGeometry(xyz,10,"FACE",ents,True)	
		if len(to_be_delete[0])>1:
			base.DeleteEntity((to_be_delete[0])[0])
			

			
		
		
		
		
		
	
	
		
		
		
	
	
	
main()


