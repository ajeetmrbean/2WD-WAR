def edit_grid(itemLocation, itemID):
    with open("views/website.html", "r") as map_file:
        filedata = map_file.read()

        filedata = filedata.replace(
            '<img id="'+itemLocation+'" src="/static/image2.png" style="width:25px;height:25px;float:left;">',
            '<img id="'+itemLocation+'" src="/static/numbers/'+str(itemID-1)+'.png" style="width:25px;height:25px;float:left;">'
        )
    with open('views/website.html', 'w') as file:
        file.write(filedata)


def display_route(route_lst):
    with open("views/website.html", "r") as map_file:
        filedata = map_file.read()

        filedata = filedata.replace(
            '<h5></h5>',
            """
            <h6>The shortest route is: %s</h6>
            <h6>The distance cost is: %s</h6>
            <h6>Time take for the calculation is: %s h, %s mins, %s s</h6>
            """ % (
                str(route_lst[0]),
                str(route_lst[1]),
                str(route_lst[2]),
                str(route_lst[3]),
                str(route_lst[4])
            )
        )
    with open('views/website.html', 'w') as file:
        file.write(filedata)

# if __name__ == "__main__":
#     edit_grid("Test")
