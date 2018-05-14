## Intro

Arcamens was designed to allow a high level of communication and collaboration by teams.
It implements so called Kanban Boards and Timelines.
Timelines can be used to delegate isolated tasks, share information, events, questions and even store information that is
pertinent to a project.

The aim of arcamens is being as flexible as possible. It allows better dealing with high payloads of information and facilitates
better organization of information. Arcamens is ideal for all kind of teams whose motto is simplicity and flexibility.

The boards, lists and cards are structured in a tree-like manner what allows a succinct perspective
of the information that is relevant to the board team.

The following image displays an example set of boards:

![arcamens-boards-0](/static/site_app/help/arcamens-boards-0.png)

After accessing the board, its lists are shown.

![arcamens-boards-1](/static/site_app/help/arcamens-boards-1.png)

Once a list is accessed by clicking on its link name it displays all the cards
that it holds.

![arcamens-boards-2](/static/site_app/help/arcamens-boards-2.png)

Arcamens boards allow one to deal with a high amount of cards in a very advantageous manner
because information is more visible. It allows one to pin certain lists that are often used
thus allowing quick access of content.

Pinning an element is as easy as clicking on the clip icon as shown below:

![arcamens-boards-3](/static/site_app/help/arcamens-boards-3.png)

**Note:** You can pin boards, lists, cards or timelines.

Arcamens makes usage of cut/copy for moving cards around, it is much more efficient than
the usual drag&drop approach.  You can cut several cards, these will stay on the clipboard
when you're ready just paste them somewhere.

### Board Creation

You can create as many boards as you desire. For creating a new board just click on Home at the navbar
and then use the popup menu by clicking the wrench icon shown at this image:

![board-creation-0](/static/site_app/help/board-creation-0.png)

You would get:

![board-creation-1](/static/site_app/help/board-creation-1.png)

One may find it necessary to have boards that are related to the same project, in such situations
it is possible to set their descriptions with a slug to group them according to their project.

Imagine you have a project named arcamens that has many plugins, you have a team for each one of the plugins.
You could come up with boards description like:



    Arcamens/Github
    Arcamens/Bitbucket
    

Then you can use your board filter with a pattern like:


    Arcamens/
    

It would display just boards that meet that slug.

**See:** Link to board filters.

### List Creation

Lists are placed inside boards, After accessing the board link name you can
create new lists for the board.

For such click on +List link button.

![list-creation-0](/static/site_app/help/list-creation-0.png)

You would get:

![list-creation-1](/static/site_app/help/list-creation-1.png)

You can set slugs for lists as well, you could handle a project with many plugins
using the approach of setting slugs for each one of your project plugins as follows:


    Bitbucket/Todo
    Github/Todo
    Bitbucket/Doing
    Github/Doing
    
    ...
    

It allows designing your project workflow without creating multiple
boards for its plugins.

### Card Creation

Card are the entities which contain actual information pieces.

Cards are created inside lists, after accessing a list just click on +Card:

![card-creation-0](/static/site_app/help/card-creation-0.png)

You would get:

![card-creation-1](/static/site_app/help/card-creation-1.png)

The card label field is used to give a short description of the task, the data field
can contain markdown content and should be used when the content is too long.
After filling the fields and creating your task, you would get the view of the card:

![card-creation-2](/static/site_app/help/card-creation-2.png)

**Note:** Click on Up to get back to the card list.

You can change all attributes for the card there, whenever an attribute is changed
then an event is fired. All users who are related to the card will get notified.
These users are those who belong to the card board or are assigned to the card.

### Events

Whenever an user creates or updates content then an event is fired. The events
are means of knowing what is going on with your teams.

![events-9](/static/site_app/help/events-0.png)

The kind of action that was performed can be commented out thus giving constructive criticism about your peers
work.

Events will carry links to the objects that are related to the user action. You can left click on the links
and inspect the cards, lists, etc in the same browser tab or just middle click and open them in new browser
tabs.

When you finished checking an user action you can mark the event as seen then it will be no longer listed in the
Events dialog but you can still access it through your logs.

### Card Workers

After a card is created it can be assigned to someone for its execution by clicking on Workers:

![card-workers-0](/static/site_app/help/card-workers-0.png)

You would get:

![card-workers-1](/static/site_app/help/card-workers-1.png)

Type a string that matches either the user name or email then hit enter.

**See:** Advanced User Search

### Board Permissions

A board will have a owner(the one who has created it), admins and members. The owner
is the only one who can make a member become an admin. Admins are allowed to add/remove members to the board
but members aren't allowed to remove peers.

For adding new members to the board(assuming you're the owner or an admin), just access the board 
then click on the wrench icon:

![board-permissions-0](/static/site_app/help/board-permissions-0.png)

Then click on Members, you would get:

![board-permissions-1](/static/site_app/help/board-permissions-1.png)

You can search users by using tag, email or name attributes.

**See:** Advanced User Search

### Tag Creation

You can tag all kind of content in arcamens, for such you need to create tags first. Everyone is allowed
to create new tags, when a tag is created an event is fired and everyone in the organization gets aware of it.

Click on the wrench icon on the organization menu:

![tag-creation-0](/static/site_app/help/tag-creation-0.png)

Then click on Tags:


![tag-creation-1](/static/site_app/help/tag-creation-1.png)

You would get:

![tag-creation-2](/static/site_app/help/tag-creation-2.png)

Notice that if your organization has many tags then you can look up a given tag by its name or description.
Just insert the pattern and hit enter then you'll get all tags that match the criterea.

Clicking on the plus sign it gives you:

![tag-creation-3](/static/site_app/help/tag-creation-3.png)

Fill the tag name and description and then click on Create.

![tag-creation-4](/static/site_app/help/tag-creation-4.png)

### Card Tags

Tags are a powerful mean of classifying content, arcamens allows you to tag cards, posts and users.
You can create as many tags as you find necessary for your organization.

### Card Task Search

### Card Search

### Organization Creation

### Timelines

### Timeline Creation

### Post Creation

### Organization Invites

### Organization Admins

### Timeline Members

### Post Workers

### Post E-mail/Notifications

### Post Tags

### Post Task Search

### Post Search

### Event Comments

### Post Filter

### List Filter

### Board Filter

### Timeline Filter

### Board Members

### Card's Text Colors

### Card Task Creation

### Card E-mail/Notifications

### Card Filter

### Card Forks

### Post Forks

### Advanced User Search

You can search users for attributes like name, e-mail or tags.

    tag:developer
 

Would list all organization users who were tagged with developer. You can combine tags as well.


    tag:developer + tag:python 


You can combine tags but mix them with other kind of attributes like name or email.


    tag:dev + @arcamens.com

Would list all workers that were tagged as developer and the email matches @arcamens.com.


![advanced-user-search-0](/static/site_app/help/advanced-user-search-0.png)

Notice that if you did:


    tag:dev + oliveira


It would list all users with the tag dev and have the string oliveira
appearing either in the name or email attributes. When you want to limit the
search to be performed under a given attribute like email you could do:


    tag:dev + email:oliveira

### Advanced Card Search

### Advanced Post Search

### Timeline Settings

### Board Settings

### Bitbucket Integration

### Organization User Removal

### Organization Settings

### Logs


