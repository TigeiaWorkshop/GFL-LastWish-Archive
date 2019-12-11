#玩家回合结束
def endOfPlayerRound():
    global round
    global isWaiting
    isWaiting = True
    round += 1
    if round == len(characters_name_list):
        resetEnemyMovingData()

#重置敌方移动数值
def resetEnemyMovingData():
    global direction_to_move
    global how_many_moved
    global how_many_to_move
    global object_to_play
    global round
    #direction_to_move 0左1上2右3下
    if sangvisFerris_data[object_to_play[round]].x > characters_data["sv-98"].x:
        if sangvisFerris_data[object_to_play[round]].y > characters_data["sv-98"].y:
            if sangvisFerris_data[object_to_play[round]].x-characters_data["sv-98"].x > sangvisFerris_data[object_to_play[round]].y-characters_data["sv-98"].y:
                direction_to_move=0
            else:
                direction_to_move=1
        else:
            direction_to_move=2
    else:
        direction_to_move=3
    how_many_moved = 0
    how_many_to_move = sangvisFerris_data[object_to_play[round]].move_range
    for i in range(1, how_many_to_move+1):
        if direction_to_move == 0:
            if map[sangvisFerris_data[object_to_play[round]].y][sangvisFerris_data[object_to_play[round]].x-i] == 0 or map[sangvisFerris_data[object_to_play[round]].y][sangvisFerris_data[object_to_play[round]].x-i] == 3:
                how_many_to_move = i-1
                break
        elif direction_to_move == 2:
            if map[sangvisFerris_data[object_to_play[round]].y][sangvisFerris_data[object_to_play[round]].x+i] == 0 or map[sangvisFerris_data[object_to_play[round]].y][sangvisFerris_data[object_to_play[round]].x+i] == 3:
                how_many_to_move = i-1
                break
        elif direction_to_move == 1:
            if map[sangvisFerris_data[object_to_play[round]].y-i][sangvisFerris_data[object_to_play[round]].x] == 0 or map[sangvisFerris_data[object_to_play[round]].y-i][sangvisFerris_data[object_to_play[round]].x] == 3:
                how_many_to_move = i-1
                break
        elif direction_to_move == 3:
            if map[sangvisFerris_data[object_to_play[round]].y+i][sangvisFerris_data[object_to_play[round]].x] == 0 or map[sangvisFerris_data[object_to_play[round]].y+i][sangvisFerris_data[object_to_play[round]].x] == 3:
                how_many_to_move = i-1
                break
    if how_many_to_move < 1:
        resetEnemyMovingData()