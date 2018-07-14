---
title: Arcamens Docs
---

### Intro

Arcamens was designed to allow a high level of communication and collaboration by teams.
It implements so called Kanban Boards and Groups.
Groups can be used to delegate isolated tasks, share information, events, questions and even store information that is
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

**Note:** You can pin boards, lists, cards or groups.

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

**See:** [Collection Filter](#collection-filter)

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

### Card Editing

After a card is created it can have its Label/Data attributes changed. Such
a change generates an event. Everyone who is attached to the card's board will
get notified as well as all workers of the card.

In order to edit/update a card just access the card and click on: Update

![card-editing-0](/static/site_app/help/card-editing-0.png)

Then you would get:

![card-editing-1](/static/site_app/help/card-editing-1.png)

After pressing Update the event will be generated and the card updated.

### Events

Whenever an user creates or updates content then an event is fired. The events
are means of knowing what is going on with your teams.

![events-9](/static/site_app/help/events-0.png)

The action that was performed can be commented on thus giving constructive criticism about your peers
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
So you will be able to add users to the card task.

**See:** [Advanced User Search](#advanced-user-search)

### Board Permissions

A board will have a owner (the one who has created it), admins and members. The owner
is the only one who can make a member become an admin. Admins are allowed to add/remove members to the board
but members aren't allowed to remove peers.

For adding new members to the board (assuming you're the owner or an admin), just access the board 
then click on the wrench icon:

![board-permissions-0](/static/site_app/help/board-permissions-0.png)

Then click on Members, you would get:

![board-permissions-1](/static/site_app/help/board-permissions-1.png)

You can search users by using tag, email or name attributes, then add users.

**See:** [Advanced User Search](#advanced-user-search)

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
You can look up the card tags by typing some pattern that shows on the tag name/description then hit enter.
It is useful when your organization has many tags.

### Card Prioritization

Arcamens implements card prioritization in a very smart and elegant
manner. You can easily prioritize a card over other cards by
specifying a consistent set of critereas. 

When a card priority changes then your board peers get
notified and the order of the cards get changed.  It is very handy when you want to make 
sure that a given task has more urgency than others.

The way of how order of cards is changed in arcamens it differs in concept
from the often used drag&drop from trello-like platforms. 

You are prompted with a list of cards that you want to increase/decrease priority from. 
You can easily filter cards based on a criterea in that list it spares a lot of time
when you want to prioritize a card over some other cards that are classified
under a given set of tags. 

The order of cards is determined by prioritization which is set as described below

Just click on the signal icon:

![card-prioritization-0](/static/site_app/help/card-prioritization-0.png)

Then you would get a list of cards that are in the list:

![card-prioritization-1](/static/site_app/help/card-prioritization-1.png)

In that dialog you can use the same usual syntax for card search. Notice
that if you have many cards in the list and you want to make sure that
the card has priority superior to a given set of cards that contain a tag
then you could do:

~~~
tag:sometag
~~~

It would list all cards with that tag thus you can easily
change card priority over other cards.

### Search for Tasks/Cards

In arcamens there is a generic concept of task, a card becomes a task when it is
assigned to someone. When the task is accomplished then one can just archive it. 
The card will remain available for later inspection.

In order to search for active or archived cards that contain bound workers to, just click on the Tasks/Cards
at the navbar:

**Note:** The mechanism will match the search pattern against all cards that can be accessed by you.

![search-for-tasks-cards-0](/static/site_app/help/search-for-tasks-cards-0.png)

From the dialog window you can search through all cards that you have access by combining
the the following options altogether with a given string pattern.

![search-for-tasks-cards-1](/static/site_app/help/search-for-tasks-cards-1.png)

**Assigned**

When it is checked then it will match against cards that are tasks. It means
cards that have at least one worker assigned to.

**Assigned to me**

When this option is checked then the filter pattern will be matched
against all cards that were assigned to you.

**Created by me**

When this option is checked then the filter pattern will match
all cards that were assigned to someone and the owner is you. Combine this filter 
with both **Assigned** or **Assigned to me** to find cards that are tasks and you have created.

**Done**

This option allows to search for archived cards instead of active ones. Combine this filter
with the previous options to find cards that were archived.

The above options when combined will produce different results for the same pattern string.
Consider you inserted the pattern:

~~~
bug + timezone
~~~

In the above pattern example it will find all cards that contain the strings 'bug' and 'timezone' 
either in the label or data attributes.  When combined with the filter options it will narrow down the matched results
according to the filter definitions so described above. 

You can get more than one match depending on the pattern and the existing cards.
Once you have filtered the cards then you can click on the card link and open it in the
actual browser tab or just right click and open in a new tab.

**See:** [Advanced Card Search](#advanced-card-search)

### Organization Creation

Organizations can serve on multiple purposes depending on the kind of business and size. 
You can map a team to an organization, a business branch to an organization or even handle all your
business team in a single organization. 

It all depends on how big your business is and on your necessities of designing your business workflow.

For creating an organization just click on your current organization icon at the navbar:

![organization-creation-0](/static/site_app/help/organization-creation-0.png)

Then click on +Organization link, you would get:

![organization-creation-1](/static/site_app/help/organization-creation-1.png)

Type your new organizatio name then click Create.

### Groups

Groups are great for sharing information, storing notes regarding a project and even delegating simple tasks.
Groups can be used as super backlogs when deaing with Scrum Methodology. As posts can be forked into cards
it allows one to setup a group to be used as a scrum board backlog.

### Group Creation

For creating a group just click on Home at the navbar then on the wrench icon at the organization
toolbar:

![group-creation-0](/static/site_app/help/group-creation-0.png)

You would get:

![group-creation-1](/static/site_app/help/group-creation-1.png)

Notice that you can associate groups to a given project by setting up a common slug.
You could fill the above fields with:

**Name:** Notes

**Description:** Arcamens/

Or you could do:

**Name:** Arcamens/Notes

**Description:** Notes on arcamens project.

There are many ways of grouping boards and groups, feel free to pick up the
best one for you. You don't need to pick a description for your boards/groups at all.

**See:** Collection Filters

After filling the fields you would get your group being listed altogether with your boards.

### Posts

Group posts can be used for multiple purposes, they can convey information about events,
tasks and even play a nice role as project notes. Snippets can be attached to posts, a snippet
can contain a title and markdown content. 

Tasks that demand one to collect information regarding a given subject can be delegated by using posts. 
The person attaches the missing information to the post as a snippet.

![post-0](/static/site_app/help/post-0.png)

Some tasks arent directly related to a specific project these tasks
can be delegated to a team or user by using a post.

![post-1](/static/site_app/help/post-1.png)

### Post Creation

After a group is created just access it then click on +Post at the group toolbar:

![post-creation-0](/static/site_app/help/post-creation-0.png)

You would get:

![post-creation-1](/static/site_app/help/post-creation-1.png)

Posts can have a short title that holds a description of the post content and
a markdown content.

After pressing Create the post will be created and every group user will get notified
of the post creation.

### Post Editing

In order to edit the contents of a post just access its timeline then click on:

![post-editing-0](/static/site_app/help/post-editing-0.png)

Then you would get:

![post-editing-1](/static/site_app/help/post-editing-1.png)

After updating the post content everyone who belongs to the board or is
an worker of the post will get notified of it.

### Post Workers

You can mention peers on a post, assign them to execute some task that's described over a group post.
A post becomes a task when there is at least a worker that is assigned to it.

Click on the Assign entry at the post toolbar in order to assign it to someone:

![post-workers-0](/static/site_app/help/post-workers-0.png)

Then you would get:

![post-workers-1](/static/site_app/help/post-workers-1.png)

Once you bind/unbind a worker to a post then the worker gets notified of it.
The worker name will be listed on the post.

### Post Tags

It is possible to tag posts for quickly finding information that is related to a given subject. Tagging a post
is as simple as tagging a card. After the post is tagged then an event is fired to all group users
and post workers.

Click on Tags entry at the post toolbar:

![post-tags-0](/static/site_app/help/post-tags-0.png)

Then you would get:

![post-tags-1](/static/site_app/help/post-tags-1.png)

### Organization Invites

An organization can contain as many users as your account plan allows. Users are invited to an organization
through e-mail. When the user is already an arcamens user then it is enough to click on the link that was sent
then join the organization. In the case his e-mail isn't belonging to an arcamens account then he will have to fill
a quick form in order to join the invite organization.

In order to send an invite just click Home at the navbar then go to the organization menu and click on the
wrench icon:

![organization-invites-0](/static/site_app/help/organization-invites-0.png)

Click on Members then you get;

![organization-invites-1](/static/site_app/help/organization-invites-1.png)

Which would list all your organization members.

Click on the plus sign at the top:

![organization-invites-2](/static/site_app/help/organization-invites-2.png)

Then fill the field with the peer e-mail to whom you would like to join your organization.

![organization-invites-3](/static/site_app/help/organization-invites-3.png)

You can check all invites that were sent by clicking on:

![organization-invites-4](/static/site_app/help/organization-invites-4.png)

You would have listed all invites:

![organization-invites-5](/static/site_app/help/organization-invites-5.png)

You can cancel invites or just resend the invite link. Notice that your account invites
can't override your account max users limit. The invites sum up with regular users and should
be lesser or equal your account max users limit.

### Organization Admins

### Group Members

Users of a group get notification from all events that happen with the group. Whenever an user
is binded/unbinded to a group everyone who is in the group gets notified.

For binding/unbinding users to a group just access the group then:

![group-members-0](/static/site_app/help/group-members-0.png)

Then you would get:

![group-members-1](/static/site_app/help/group-members-1.png)

From there you can search users from your organization that match a given criterea.

**See:** [Advanced User Search](#advanced-user-search)


### Post E-mail/Notifications

When a post has workers who were assigned it may be interesting to call attention
of these workers through e-mail. A link for the post would be sent through e-mail
with a message.

![post-email-notification-0](/static/site_app/help/post-email-notification-0.png)

You can click on the worker name and then:

![post-email-notification-1](/static/site_app/help/post-email-notification-1.png)

After clicking on Request attention through e-mail you would be prompted with:

![post-email-notification-2](/static/site_app/help/post-email-notification-2.png)

Fill the form and send the e-mail notification.

You can as well send notification to all post workers by clicking on Alert Workers.

### Post Prioritization

Arcamens groups can play the role of backlogs where it can be used
with scrum methodology, groups can also be used for isolated task delegation.

Prioritization of posts work alike the one for cards, when a given post
is prioritized then an event is generated and everyone who is in the post's group
gets notified.

For doing prioritization of a given post just access the group
then click on the signal icon at the post:

![post-prioritization-0](/static/site_app/help/post-prioritization-0.png)

Then would get a list of posts that are in that group:

![post-prioritization-1](/static/site_app/help/post-prioritization-1.png)

Imagine that you had a long product backlog with 200 posts that are correctly classified
with tags. What if you wanted to just prioritize a given post that corresponds to a bug fix over all other posts
that correspond to features? Well, you can just use the post filter pattern language
to select all posts that contain the tag bug:

~~~
tag:bug
~~~

That is just a simple case you could have a lot of many other
possibilities. 

Using this approach for prioritization of posts/cards rather than the usual
drag/drop thing it allow to improve work quality and productivity because
correct ordering of priorities can be done more accurately.

You can change the post priority up/down some other card to make it explicit
to your group peers the correct order of tasks execution. You should
also notice that prioritizing posts change the displaying order of the posts.

### Search for Tasks/Posts

Posts are similar to cards in some ways, when a post is created
then it becomes a task when it is assigned to someone.

In order to search for posts that are assigned to someone or not just click
on Tasks/Posts at the navbar.

![search-for-tasks-posts-0](/static/site_app/help/search-for-tasks-posts-0.png)

Then you would get:

![search-for-tasks-posts-1](/static/site_app/help/search-for-tasks-posts-1.png)

The option **Assigned** when  checked would match against posts
that have at least one worker assigned to. It means that it matches just
against posts that are tasks.

The option **Assigned to me** would perform the search pattern through
all tasks that someone has assigned to you.

If you option for  **Created by me** then it would check the pattern against all posts
that you created and it was at least one worker binded to.

Consider you wanted to search for posts that contain the strings 'form', 'html' and 'need a snippet'
either in the label or data attribute. After inserting that pattern you could combine
with the so described filter options above.

Notice that the order of strings is not relevant; You could also try:

~~~
need a snippet + form + html
~~~

Which would work alike.

**Note:** Leave the Done attribute checked for searching only through the archived posts.

**See:** [Advanced Post Search](#advanced-post-search)

### Event Comments

All kind of user actions in Arcamens are liable of being commented. Whenever an user
assigns a worker to a post it generates an event then the event/action can be commented out.

When an user action is commented then another event is generated but it doesn't allow
comments for action comments.

Click on Events at the navbar:

![event-comments-0](/static/site_app/help/event-comments-0.png)

Then you would get:

![event-comments-1](/static/site_app/help/event-comments-1.png)

By clicking on the event Comments link:

![event-comments-2](/static/site_app/help/event-comments-2.png)


The users who are related to the event would get a new event like:

![event-comments-3](/static/site_app/help/event-comments-3.png)

They can reply by clicking on the event Comments link.

### Post Filter

It is possible to filter group posts as well, whenever you access the group
then it will list just posts that match the filter pattern.

For such just access the group then click on Filter at the group menu:

![post-filter-0](/static/site_app/help/post-filter-0.png)

You would get:

![post-filter-1](/static/site_app/help/post-filter-1.png)

It is mostly useful for filtering posts based on tag, owner or workers but it works
with simple patterns as well.

Would list all posts that have both tags.

    tag:feature + tag:bug

    
Would list all posts whose owner's email or name matches the string 'last.src':


    owner:last.src


Listing posts that has a specific worker:


    worker:last.src


Would list all posts that have two workers whose name/email matches both strings.

    worker:last.src + worker:porton


**See:** [Advanced Post Search](#advanced-post-search)

### Collection Filter

Groups and boards can be grouped by subject/project, it allows to form collections of boards/groups.
One could have a project that has many plugins and keep a board for each one of its plugins.

It is necessary to stabilish a naming convention for your boards/groups. 

For example:

    Group: Arcamens/Notes

    Board: Arcamens

    Group: Arcamens/News

    Group: Arcamens/Bugs


All these objects have a common pattern in its name. As arcamens allows to setup filter for boards/groups 
then if you want to view just boards or groups that are related to a given subject it gets simple.

Just click Home at the navbar and click on the Filter link at the organization menu:

![collection-filter-0](/static/site_app/help/collection-filter-0.png)

You would get:

![collection-filter-1](/static/site_app/help/collection-filter-1.png)

In the previously stated context if you typed the string 'Arcamens' then you would view
all the boards/groups that contain such a string either in its name or description.

### Card Colors

When a card is a task it displays as green:

![card-colors-0](/static/site_app/help/card-colors-0.png)

When a card is assigned to you then it displays as red:

![card-colors-1](/static/site_app/help/card-colors-1.png)

A card fork's background is lighter than the usual card as well:

![card-colors-2](/static/site_app/help/card-colors-2.png)

### Card E-mail/Notifications

When a card is created and it has workers bound then it is possible to send
e-mail notifications to the card workers.

For such just access the card then click on the card worker name:

![card-email-notification-0](/static/site_app/help/card-email-notification-0.png)

You'll get:

![card-email-notification-1](/static/site_app/help/card-email-notification-1.png)

After clicking on **Request Attention through e-mail** you would get:

![card-email-notification-2](/static/site_app/help/card-email-notification-2.png)

You can fill with some message to be sent to the user.

When the card has many workers you can just click on the **Alert workers?** link
then sending an alert to all card workers at once.

### Card Filter

You can specify a pattern for filtering cards inside lists as well thus allowing one to view just cards
that have attributes matching requirements.

Access the desired list then click on Filter at the list menu:

![card-filter-0](/static/site_app/help/card-filter-0.png)

You would get:

![card-filter-1](/static/site_app/help/card-filter-1.png)

You can filter by tag, worker, owner etc.

**See:** [Advanced Card Search](#advanced-card-search)

### List Filter

### Card Relations

### Card Forks

When a given task can't be executed at once then it is necessary
to break it into multiple subtasks. In Arcamens it is named card forking, 
when you fork a card you create a link between both cards.

Consider the card below:

![card-forks-0](/static/site_app/help/card-forks-0.png)

In order to fork such a card just click on : Fork/Card link then you would get:

![card-forks-1](/static/site_app/help/card-forks-1.png)

When there are many lists you can just filter the lists based on a pattern:

![card-forks-2](/static/site_app/help/card-forks-2.png)

**Note:** If you wanted to search for a list named "beta" that is in a board named "alpha"
then you could do:

~~~
alpha + beta
~~~

Notice that if you inserted just the list name it would output more results if you have other lists named like this. 
It is also important to notice that the above pattern would match all lists that either board name
or list name contains each one of the strings "alpha" and "beta". 

For more consistent results just use:

~~~
board:alpha + name:beta
~~~

It would make sure to list just a list from a board that contains the string "alpha" in its name
and the list name contains the string "beta".

Once you pick up the desired list you will get the fork creation dialog:

![card-forks-3](/static/site_app/help/card-forks-3.png)

If you click on **Keep old content** link it will fill the fields with the parent card
attributes. It is useful sometimes when you just want to fork and edit the previous task.

After forking you'll get:

![card-forks-4](/static/site_app/help/card-forks-4.png)

You can browse all forks and parents of a given card by following the
links on the card.

**Note:** You can open a given card in a new browser tab by just right clicking it then open in a new tab.

**See:** [Advanced List Search](#advanced-list-search)

### Switch Card Parent

### Post Forks

Group posts can be forked into cards, it is mostly useful when a group is used
as a kanban board backlog. 

Groups are great for sharing information of all kind, one might use a group
to get bug reports and fork the bug reports into card tasks over their
corresponding project boards. It all depends on how you feel more comfortable
to model your team workflow. 

For forking a post just access the post:

![post-forks-0](/static/site_app/help/post-forks-0.png)

After that just click on: Fork/Card it would give you:

![post-forks-1](/static/site_app/help/post-forks-1.png)

For basic understanding on how to filter lists:

**See:** [Card Forks](#card-forks)

After picking up the desired list you would get:

![post-forks-2](/static/site_app/help/post-forks-2.png)

After creating the card then everyone who is attached to the group
and to the destin list's board will get notified of the fork creation.

Some features that should be implemented may be related to multiple project boards, 
the forking mechanism allows a fancy approach for keeping track of all tasks
that are necessary in order to have a given feature implemented.

For a more complete reference on list filters:

**See:** [Advanced List Search](#advanced-list-search)

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

Arcamens has a powerful pattern filtering language, it allows one to quickly
write filter patterns to perform searches based on card attributes.

The sign '+' plus is used to mix up card attributes for filtering. The general format
of a search pattern consists of:

~~~
Attribute0:Value1 + Attribute1:Value2 + ...
~~~

The following attributes are accepted when searching for cards:

**Owner**

The user who has created the card.

Example:

~~~
owner:oliveira
~~~

Would match all cards whose owner name or email contains the string 'oliveira'.

Thus consider a worker whose name and email are registered as follow:

~~~
Name: Iury de Oliveira Gomes Figueiredo
E-mail: iogf@arcamens.com
~~~

The so defined pattern above would list all cards which were
created by that worker as well.

Notice that by using the above pattern it would list cards
created by a worker whose name or e-mail consists of:

~~~
Name: John Rambo
E-mail: oliveira@arcamens.com
~~~

In order to make your search more strict it is enough to add more information, like in:

~~~
owner:oliveira@arcamens.com
~~~

Would work like a charm.

**Label**

The card short description. Imagine that you have a card
whose label/title is:

~~~
Update the password list used by CommonPasswordValidator to a more recent list
~~~

If you wanted to write a possible pattern filter to match against that card then you could
do:

~~~
label: update
~~~

But also notice that despite of the above pattern being enough to list that card
in the search it is not enough to make the results strict. It would list a lot of cards
that contain the string 'update' in its short description.

In order to improve your results you can just add more information like:

~~~
label: update the password
~~~

It could do the job in case you remembered better how the card label was written. However
very often we just remember a few informations regarding the card, in these situations
you could merely do:

~~~
label:update + label:pass + label:validator
~~~

It would surely find all cards that contain the string 'update' in its label
and the string 'pass' as well as the string 'validator'. It would probably be enough
to find the desired card

More interestingly it could be possible to do:

~~~
label:update the password + label:commonpasswordvalidator to a more
~~~

The above one is left just as a matter of better elucidating the reader
of the workings of the pattern filtering language mechanism.

**Data**

The card data it is the field that contains markdown.

In order to demonstrate the data attribute usage in searches, consider
the existance of a card that is written as follows:

~~~
Label: Add an option to django-admin to always colorize output

Data: With Django management commands, it is currently possible disable colors with the --no-colors flag.
What I'd like to have is basically the other side of the coin: a --force-colors flag that instructs 
Django to output ANSI color sequences in cases it would disable colors by default (typically, 
when the output is piped to another command, as documented).

My real world use-case is the following one: I have a custom Django command to import data. 
I run this command myself, and I'd like to send a colored log (HTML seems perfect for this) to the data curators. 
I can use the ​https://github.com/theZiz/aha utility for this, but that doesn't work since Django disable colors when the output is piped.
Other nix commands have a special flag for this exact use-case, for example $ ls --color=always

~~~

The above tag maps to a real issue taken from: https://code.djangoproject.com/query

Imagine that you wanted to look that card up and you remembered just a few details regarding its description.
The details are the string 'django' and that it is related to its management command feature and it is related to coloring output.

Well, in that case you could quickly come up with:

~~~
data:django + data:management command + data:color
~~~

That probably be enough to bound your results in a reasonable amount of cards whose
inspection would be feasible to do. In case you had many other cards with the same strings
showing up in the data field then you could just try adding more information in order to narrow
down your results.

Note that if you knew details about the card label then you could also do:

~~~
label:django-admin + data:django + data:management command + data:color + label:colorize output
~~~

You would probably never face a situation where you would need to insert such a long pattern
to find your cards, it is just left as a matter of examplification.

Notice also that when you're searching for cards based on the label/data attribute then it is not
necessary to use the verbose format as above, it could be written like:

~~~
django-admin + django + management command + color + colorize output
~~~

Which would be give similar results to the previous filter pattern. You use the verbose format regarding label/data:

~~~
data:value
~~~

Only when you want to specifically mean that the card contains the pattern string in the data
but not in the label or vice versa. It is not very often useful at all, better to use the less
prolix format as shown above when matching against label or data attributes of cards.

**Tag**

It allows to search for cards based on its tags. Imagine that you wanted
to list all cards that contain a given set of tags, it is when you use the tag
attribute.

Consider you wanted to find all cards that contain the tags: python, feature and arcamens.
You could just write:

~~~
tag:python + tag:feature + tag:arcamens
~~~

It is important to notice that as all other card attributes it can be mixed up.

Thus it would as well be a valid filtering pattern:

~~~
label:django admin + tag:python + tag:feature + tag:arcamens + data:command management
~~~

**Worker**

Find cards that are assigned to a specific worker. This is such
a very handy card attribute, you'll find yourself looking up cards
that are assigned to some of your peers very often.

Imagine you wanted to look up all cards that are assigned to the worker John Rambo
and are also tagged with the following tags: vy and untwisted

You could just write:

~~~
tag:vy + worker:rambo + tag:untwisted
~~~

If you also wanted to find cards that are assigned to both Rambo and Porton workers
then you could do:

~~~
worker:rambo + worker:porton
~~~

Notice also that you can use the worker email as a value for the worker attribute:

~~~
worker:rambo@arcamens.com + worker:porton@arcamens.com
~~~

**List**

Filter cards that belong to a list whose name contains
some string. It is a very common situation to inspect cards
that are over specific lists from your boards. 

Imagine you wanted to list all cards that are over the list Todo, then
you could do:

~~~
list:Todo
~~~

More interestingly you could do things like:


~~~
tag:bug + list:todo
~~~

Would find all cards that are on a list whose name matches the string 'todo' and are also tagged
with the tag bug.

If you wanted to list all cards that are over the lists whose name matches Done and are
assigned to a worker named Rambo then you could do:

~~~
worker:rambo + list:done
~~~

**Board**

Filter cards whose board name contains some string. Imagine you wanted
to narrow down your results by including the cards board then you would use
this attribute.

The below example would match against cards that are from a board whose
name or description contains the string 'arcamens'.

~~~
board:arcamens + tag:bug
~~~

It would find all cards that are tagged as related to bugs and are from boards
where the string 'arcamens' shows up.

**Created**

Filter cards based on its creation date. List cards based on its
creation date:

~~~
created:2018
~~~

Would find all cards that were created in 2018.

~~~
created:2018-05-23
~~~

The above example would find all cards that were created on 2018-05-23.
The general format is: year-month-day

For finding cards created in the month 05 then do:

~~~
created:-05-
~~~

**File**

Filter cards whose one of its attachments contains some string. Imagine you wanted
to find a card that has a given pdf file attached to.

The file will contain the string '.pdf' showing in its name thus you could do:

~~~
file:.pdf
~~~

Would be enough to find all cards that have attachments that are pdf.

If you wanted to look up a card that has two attachments: engine tutorial.pdf, ui features.jpg

Then you could do:

~~~
file:engine + file:features
~~~

That would be enough to find your card, if you wanted to be omre specific
you could just do:

~~~
file:engine tutorial + file:ui features.jpg
~~~

**Note**

Filter cards that have a note whose title or data attribute
contains a given string. This attribute is useful to find cards
when you remember some characteristics of one of its notes.

Imagine you had a card that had the following note attached to:

~~~
Hi Nicolas. I'm going to Accept this: it seems reasonable. 
…in cases it would disable colors by default (typically, when the output is piped to another command, as documented).
Can I ask, where is this documented? I cannot seem to find it. Thanks.
~~~

Then you could merely come up with the pattern:

~~~
note:color + Note:output + note:documented
~~~

Notice that you could also do:

~~~
note:going to accept + note:seems reasonable
~~~

**Note Owner**

If finds all cards that have a note whose creator name or email
contain a string. Imagine you wanted to find all cards
that have at least one note created by a given worker then you could do:

~~~
note.owner:rambo
~~~

Or you could do:

~~~
note.owner:rambo@arcamens.com
~~~

To be more specific.

**Note File**

It matches against all cards that have a note with an attachment file
whose name contains a specific string.

The above attribute works alike the one for card attachments but regards
note attachments.

~~~
note.file:.pdf + note.file:ui.jpg
~~~

Would find all cards that have at least a note with attachment files
whose names contain the strings '.pdf' and 'ui.jpg'.

**Fork**

Filter cards that have a fork whose label or data attribute contains
a givein string.

Imagine the situation that you want to find cards based on the label/data attribute
of its forks, it is when you would use such a card attribute.

~~~
fork:django admin + fork:markdown
~~~

That would match all cards that contain a given fork whose label or data attribute
contain the strings 'django admin' and 'markdown'.

**Fork Tag**

Filter cards that have a fork that is tagged with a given tag.

This would be useful to filter cards whose forks are tagged with a given set of tags.

~~~
fork.tag:bug
~~~

That would find all cards that have a fork that is tagged with bug tag.

**Fork Worker**

Filter cards that have a fork whose worker name or email contain
a given string.

This pattern:

~~~
fork.worker:rambo
~~~

Would find all cards that have a fork thats assigned to the worker Rambo.

**Parent**

Filter cards that have a parent card whose label or data attribute
contains a given string.

This card attribute is useful to list all forks of a given card, suppose you know
a card that is as follow:

~~~
label: SQLite and Queryset.iterator() support
data: I’m writing a non-web app that uses Django as the ORM and SQLite as the backend, 
and I have a need to iterate over large tables efficiently.

 Django’s documentation says Queryset.iterator() does not work on SQLite (1) (2) but I tried it anyways, and discovered that it works: 
results are not read into memory in entirety, but streamed from the database in chunks. 
I traced this to an apparent logic error in the SQLCompiler.execute_sql()
method (3) and the interpretation of the can_use_chunked_reads flag. More on this below.
~~~

Suppose it had like more than three layers of forks then you wanted to list all of its forks:

~~~
parent:sqlite and queryset.iterator
~~~

That would be enough to list all of the desired forks.

**Parent Tag**

The same as fork tag but regarding its parent card.

This one lists forks whose parents contain a given set of tags.

~~~
parent.tag:bug + parent.tag:django
~~~

That pattern would list all forks whose parent contains the tags bug and django.

**Parent Worker**

The same as fork worker but regarding its parent card.

The below pattern:

~~~
parent.worker:iury
~~~

Would find all card forks whose parent is assigned to the worker name or email contains
the string 'iury'.

### Advanced Post Search

Group posts share some attributes with cards, these are:

**Owner**

The post creator.

**Worker**

Relative to the post workers.

**Tag**

Match against the post tags.

**Created**

Regarding the post creation date.

**Label**

The post title.

**Data**

The post data attribute, it is the one that carries markdown.

**Fork**

The card forks of the post in case it has sub tasks
that are spreaded over boards.

In order to get additional information about the above attributes.

**See:** [Advanced Card Search](#advanced-card-search)

In addition to cards the posts can have the following different attributes:

**Snippet**

It allows one to match against posts that contain a given string either in the title
or in the data attribute.

Imagine you want to find a post which contains a snippet whose title is:

~~~
A snippet how to use gle aka google searcher library for python.
~~~

And its data field contains:

~~~
from gle import Google

# Count is the number of pages that you want to extract results.
x = Google(count=2)
pages = x.search('python vy editor')

for indi in pages:
    for indj in indi:
        print(indj)
~~~

Then the below filter pattern would do the job to find such a post.

~~~
snippet:use gle + snippet:x.search
~~~

**Snippet Title**

The above attribute matches strictly the snippet title.

~~~
snipet.title:some string in the title
~~~

**Snippet File**

This one matches against posts that have snippets with attachments.

~~~
snippet.file:engine.pdf 
~~~

That would find all posts that have a snippet with an attachment whose filename contains
the string 'engine.pdf'.

**Snippet Owner**

This one is regarding the snippet creator.

~~~
snippet.owner:Norris
~~~

Would find all posts that have at least one snippet that was created by a guy
named Norris.

**Group**

It narrows down the results by including posts from a specific group.

~~~
group:arcamens/backlog
~~~

Would match against posts that are from a group named 'arcamens/backlog'.

### Advanced List Search

When forking cards/posts it is necessary to search the desired
board list that will contain the fork. Lists are searched pretty much
like cards/posts except that it contains some different attributes.

List attributes used in searches:

**owner**

The one who has created the list.

**name**

The name of the list.

**board**

The board that contains the list.

**description**

The list description.

When no attribute is specified then the default attributes
that are assumed consist of the board name and list name.

For example:

~~~
arcamens + todo
~~~

The above pattern would match all lists that contains
each one of the strings either in the board name or list name.
So, if there were a list named Todo in a board named Arcamens
then it would be listed.

Suppose you wanted to list all lists whose owner is a guy named iury and
it is named Todo:


~~~
owner:iury + name:todo
~~~

**Note:** When the owner attribute is used then it matches against the owner name and e-mail.

If you wanted to search all lists based on description then you could do:

~~~
description:contain bugs
~~~

It would list all lists that contains the string 'contain bugs' in its description.
When searching by using the description attribute it is mostly useful if you have
a project with many plugins and you're handling all your plugins insde the project board.

The naming scheme examplifies the situation:

~~~
Arcamens
    Name:Todo
    Description:core_app
    .
    .
    .

    Name:Todo
    Description:bitbucket_app

    Doing
    Description:bitbucket_app

    Done
    Description:bitbucket_app

    To check
    Description:bitbucket_app


    .
    .
    .
~~~

Imagine you wanted to fork a given card from core_app/Todo list
into bitbucket_app/Todo list:

~~~
arcamens + description:bitbucket
~~~

That would be enough to list all lists from board arcamens whose description
contains the slug string 'bitbucket'.

You could as well do:

~~~
board:arcamens + description:bitbucket
~~~

Which would give you more accurate results in case you have other boards where the string
'arcamens' shows in.

### Group Settings/Removal

You can rename a group or delete it, you just access the desired group
then click on Settings at the group menu:

![group-settings-0](/static/site_app/help/group-settings-0.png)

You would get:

![group-settings-1](/static/site_app/help/group-settings-1.png)

From there you can change the group attributes like name/description.

You can as well click on Delete then you'll be asked for confirmation. 
Type the group name then press Delete.

### Board Settings/Removal

You can rename a board by accessing its settings form. For such just access the board
then click on the wrench icon:

![board-settings-0](/static/site_app/help/board-settings-0.png)

Click on Settings then you get:

![board-settings-1](/static/site_app/help/board-settings-1.png)

From there you can as well delete the board, you'll be asked for confirmation.

### Bitbucket Integration

### Organization User Removal

In order to remove an user from an organization it is necessary to be admin of the organization.
The one who is removing the user will own all timeliens and boards of the removed user.

Click on the wrench icon at the organization menu:

![organization-user-removal-0](/static/site_app/help/organization-user-removal-0.png)

Then click on Members, you would get:

![organization-user-removal-1](/static/site_app/help/organization-user-removal-1.png)

### Organization Settings/Removal

Click on wrench icon at the organization menu then Settings:

![organization-settings-removal-0](/static/site_app/help/organization-settings-removal-0.png)

You would get:

![organization-settings-removal-1](/static/site_app/help/organization-settings-removal-1.png)

### Logs

After an event is marked as seen it gets available through the logs window. In the logs
window you can filter logs based on date.It is mostly useful to check what has been done
in a period of time.

For inspecting your logs just click on your name at the navbar and click on Logs.

![logs-0](/static/site_app/help/logs-0.png)

Then you would get:

![logs-1](/static/site_app/help/logs-1.png)

From there you can specify the starting/ending date to filter your
logs.










