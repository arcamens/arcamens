## Intro

Arcamens was designed to allow a high level of communication and collaboration by teams.
It implements so called Kanban Boards and Timelines, the latter can be used for multiple purposes. 
They can be used to delegate isolated tasks, share information, events, questions and even store information that is
pertinent to a project.

The aim of arcamens is being as flexible as possible. It allows better dealing with high payloads of information and better organization of 
information. Arcamens is ideal for all kind of teams whose motto is simplicity and flexibility.

The boards, lists and cards are structured in a tree-like manner it allows a succinct perspective
of the information that is relevant to the board team.

![arcamens-boards-0](/static/site_app/help/arcamens-boards-0.png)

After accessing the board it is shown its lists.

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

You can create as many boards as you desire. For creating a new board just click on Home at the navbar then

![board-creation-0](/static/site_app/help/board-creation-0.png)

You would get:

![board-creation-1](/static/site_app/help/board-creation-1.png)

One may find it necessary to have boards that are related to the same project, in such situations
it is possble to set their descriptions with a slug to group them according to their project.

Imagine you have a project named arcamens that has many plugins, you have a team for each one of the plugins.
You could come up with boards description like:



    Arcamens/Github
    Arcamens/Bitbucket
    

Then you setup your board filter with a pattern like:


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

After binding/unbinding a given user to a board he/she will get notified of it.

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
For tagging a given card just access the card by clicking on its label link.

![card-tags-0](/static/site_app/help/card-tags-0.png)

Then you'll view the card attributes.

![card-tags-1](/static/site_app/help/card-tags-1.png)

Click on Tags button at the card toolbar:

![card-tags-2](/static/site_app/help/card-tags-2.png)

Then you'll be able to manage the card tags:

![card-tags-3](/static/site_app/help/card-tags-3.png)

If you add/remove a tag to a card then everyone who is related to the card will get notified. 
The card board members and card workers.

You can look up the card tags by typing some pattern that shows on the tag name/description then hit enter.
It is useful when your organization has many tags.

### Card Task Search

### Card Search

### Organization Creation

### Timelines

Timelines are great for sharing information, storing notes regarding a project and even delegating simple tasks.
Timelines can be used as super backlogs when deaing with Scrum Methodology. As posts can be forked into cards
it allows one to setup a timeline to be used as a scrum board backlog.

### Timeline Creation

For creating a timeline just click on Home at the navbar then on the wrench icon at the organization
toolbar:

![timeline-creation-0](/static/site_app/help/timeline-creation-0.png)

You would get:

![timeline-creation-1](/static/site_app/help/timeline-creation-1.png)

Notice that you can associate timelines to a given project by setting up a common slug.
You could fill the above fields with:

**Name:** Notes

**Description:** Arcamens/

Or you could do:

**Name:** Arcamens/Notes

**Description:** Notes on arcamens project.

There are many ways of grouping boards and timelines, feel free to pick up the
best one for you. You don't need to pick a description for your boards/timelines at all.

**See:** Collection Filters

After filling the fields you would get your timeline being listed altogether with your boards.

### Posts

Timeline posts can be used for multiple purposes, they can convey information about events,
tasks and even play a nice role as project notes. Snippets can be attached to posts, a snippet
can contain a title and markdown content. 

Tasks that demand one to collect information regarding a given subject can be delegated by using posts. 
The person attaches the missing information to the post as a snippet.

![post-0](/static/site_app/help/post-0.png)

Some tasks arent directly related to a specific project these tasks
can be delegated to a team or user by using a post.

![post-1](/static/site_app/help/post-1.png)

### Post Creation

After a timeline is created just access it then click on +Post at the timeline toolbar:

![post-creation-0](/static/site_app/help/post-creation-0.png)

You would get:

![post-creation-1](/static/site_app/help/post-creation-1.png)

Posts can have a short title that holds a description of the post content and
a markdown content.

After pressing Create the post will be created and every timeline user will get notified
of the post creation.

### Post Workers

You can mention peers on a post, assign them to execute some task that's described over a timeline post.
A post becomes a task when there is at least a worker that is assigned to it.

Click on the Assign entry at the post toolbar in order to assign it to someone:

![post-workers-0](/static/site_app/help/post-workers-0.png)

Then you would get:

![post-workers-1](/static/site_app/help/post-workers-1.png)

Once you bind/unbind a worker to a post then the worker gets notified of it.
The worker name will be listed on the post.

### Post Tags

It is possible to tag posts for quickly finding information that is related to a given subject. Tagging a post
is as simple as tagging a card. After the post is tagged then an event is fired to all timeline users
and post workers.

Click on Tags entry at the post toolbar:

![post-tags-0](/static/site_app/help/post-tags-0.png)

Then you would get:

![post-tags-1](/static/site_app/help/post-tags-1.png)

### Organization Invites

### Organization Admins

### Timeline Members

Users of a timeline get notification from all events that happen with the timeline. Whenever an user
is binded/unbinded to a timeline everyone who is in the timeline gets notified.

For binding/unbinding users to a timeline just access the timeline then:

![timeline-members-0](/static/site_app/help/timeline-members-0.png)

Then you would get:

![timeline-members-1](/static/site_app/help/timeline-members-1.png)

From there you can search users from your organization that match a given criterea.

**See:** Advanced User Search


### Post E-mail/Notifications

### Post Task Search

### Post Search

### Event Comments

### Post Filter

### Collection Filter

### Card's Text Colors

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

You can rename boards by accessing its settings form. For such just access the board
then click on the wrench icon:

![board-settings-0](/static/site_app/help/board-settings-0.png)

Click on Settings then you get:

![board-settings-1](/static/site_app/help/board-settings-1.png)

From there you can rename or change its description.

### Board Deletion

### Bitbucket Integration

### Organization User Removal

### Organization Settings

### Logs



