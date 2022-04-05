# MyGarden

Welcome to MyGarden! This a web application that helps users keep track of their plants and all garden-related tasks. All you need to do is make an account, and you're ready to start!

## Background

MyGarden is built using a Flask framework in Python. Data is stored in a SQLite database by using the CS50 Python library.

## Usage

To start using MyGarden, you first need to register for an account:
![registration page](/images/register_page.png)

You should then be taken to the homepage, which will display your Plants and Tasks (it won't display anything at this point because you're a new user!)
![home page](/images/home_page1.png)

To start adding plants to your account, click the more button or the Plants tab in the navbar, then press add.
![plants page](/images/plants_1.png)

You'll be taken to a page where you can put the plant name and number of plants. The notes section is optional.
![adding a plant](/images/add_plant.png)

Congradulations! You've added your first plant! A card should show up on the plants page with the plant you just added.

To edit any of your plants, click edit, then select the plant you'd like to edit from the dropdown.
![choose a plant to edit](/images/edit_plants_dropdown.png)

You should be taken to a page similar to the add page, but with the plant information filled out. When you save your changes, the plant edited should show up at the top of the plants page.

To delete a plant, click delete. You'll be taken to a page with a dropdown where you can choose the plant to delete.
![deleting a plant](/images/delete_plant.png)

Now that you've added some plants, it's time to add tasks! Click on the Tasks tab in the navbar to start.

Adding, editing, and deleting tasks works similarly to the Plants page. The main difference is that you can assign tasks to any plant you've added to your account! Adding a task also gives you the option to include the start date, time, and any repeats.
![adding a task](/images/add_task.png)

And that's it! Now can view your plants and tasks from their respective pages or from the homepage!
![home page](/images/home_page2.png)

The next time you want to view or modify your plants or tasks, log in with the email and password you used to register. You can only use an email once to register an account.

## Author

Olivia Shen

## Note
This was my final project for CS50x 2020.
