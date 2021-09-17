from modules.entity_readers.helpers import *

def read_MultiPanel(f):
	'''
	Multipanel (0x1f = 31) 01111100
	41 entities. Note: treehouse bridges are not Multipanels.
	- node_ids can point to a Door entity, I guess if completing the set triggers the opening of the door?
	- the ids in node_ints can be ids of Door entities
	- all Multipanel entities have a list of ints in node_ints.
	'''
	# TODO: check the Multipanel that use the same mesh, and verify that the inclination of the panels (rotation on the row's axis) is the same, cause it could be one of the unexplained numbers.
	# unexplained fields: 0, 6, 11
	return (
		read_float32(f),				#  0: Can be:
										#     - 0.5 for the first set in symmetry island (reflect_touch*), the pairs of puzzles guarding the cement factory (but not those of the sawmill which look exactly the same),
										#       the two exit doors of the marsh (shapers_come_together* and contemplation*), and the hub (no-)sound puzzles.
										#     - 0.8 or 0.85 for the others
		read_optional_string(f),		#  1: The basename of a mesh file for the panels: the actual mesh files have the number of puzzles in the mesh added to the base filename and an extension.
		read_id(f),						#  2: Can be None, a Power_Cable, a Door, or a Machine_Panel. -> The entity powered by solving all puzzles in the row? (not the "last puzzle", because some rows can be solved in any order)
		read_int(f),					#  3: Always -1.
		read_list(f, read_id),			#  4: The list of Machine_Panel entities that define the puzzles in the row. Never empty.
		read_byte(f),					#  5: Boolean. Always set, except for #7 (fade*, the row in symmetry island with the disappearing line) -> is it just for the disappearing line?
		read_float32(f),				#  6: In the range [0.0-1.0] although only the red pool set in the marsh is 1.0 and all others are 0.3 or under (most are 0.1).
		read_byte(f), 					#  7: Boolean. Only set for the three sets of symmetry island, the second row of the cement factory, the first row of the saw mill, the melted row of the glass factory,
										#     and the row with disconnected polyominos in the marsh.
										#     -> These rows are completed from right to left instead of from left to right.
		read_byte(f),					#  8: Boolean. Only set for the two puzzles at the entries of the sawmill and cement factory, the puzzles in the red pool of the marsh, the two with(out) sound in town.
										#     -> For these rows, all puzzles are powered from the start instead of being powered when the previous one is solved.
		read_byte_array(f,4),			#  9: I don't know what this is. It looks like the data in Machine_Panel field 32.
										#     All puzzles that have a same value for this field have the same number of puzzle but the reverse is not always true.
										#     -> Actually, puzzle with the same value in this field have the same values in the next field for the groups matching puzzles in the row, so I guess it could be a CRC.
										# 10: Ten similar groups of 7 floats.
										#     In a group, 4th float indicates if there is data in the group (1.0) or not (0.0).
										#     The groups containing data always precede the empty groups (filled with 0.0), and there are always at least as many groups with data than there are puzzles in the row.
										#     Note that no multipanel in the game has more than 9 puzzles (reached only by the segregation rule tutorial), so the number 10 garanties there is an unused group.
										#     -> actually, I think data in groups past the number of puzzles in the row is copy-paste garbage that has not been 0-ed and should be ignored.
										#     1st float is usually constant for all puzzles in the row and slight variations match the unaligned puzzles.
										#     2nd float seem to be the position of the puzzle on the row axis (used in autofocus mode).
										#     3rd float is often 0.0 but can take values between -0.0266 and 0.0031. Usually the same value for all groups, but there are exceptions.
										#     -> 1-2-3 seem to be a vector giving the position of the puzzle, or more likely, of the autofocus camera position.
										#     4th is always 1.0, 5th and 6th floats are always null. -> 4-5-6 might be a normal to the surface or the direction to look to
										#     7th float is always between 0.6 and 0.7 if present. -> field of view? (as radians, it would give angles of 34° to 40°).
		read_array(f,10,lambda src: read_array(src,7,read_float32)),	
		read_byte(f),					# 11: Boolean. Only set for the challenge clock that is in the room of the record player.
		read_byte(f),					# 12: Boolean. Only set for the three challenge clocks. (for the dot in the start circle? Or because there is no autofocus on these ones?)
										#     -> probably not for the circle has the keep platforms have a similar design, the inner circle being only filled if the puzzle is solved.
		read_byte_array(f,4),			# 13: Always 0.
	)
