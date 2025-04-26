package com.xuanmanhdao.newsservice.entity;

import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.Id;
import org.springframework.data.elasticsearch.annotations.Document;

@Document(indexName = "news")
@Getter
@Setter
public class NewsDocumentEntity {
    @Id
    private String url;
    private String source;
    private String title;
    private String image;
    private String body;
}
